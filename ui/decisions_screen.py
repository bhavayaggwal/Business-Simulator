"""Decisions: set this month's price, marketing and stock purchases."""
from decimal import Decimal, InvalidOperation

from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton

from logic import validation
from ui.soft import SoftCard
from ui.style import fmt_money, fmt_units
from ui.widgets import FormField, InfoLabel, Screen, card, repolish, rule, section


class DecisionsScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Decisions",
                         "Set your price, marketing and stock for the month ahead, then "
                         "simulate it to see what happens.")
        g = app.glossary
        columns = QHBoxLayout()
        columns.setSpacing(4)

        # Left card: the three decisions
        form_card, form = card(spacing=10)
        form.addWidget(section("This month's decisions"))
        self.price = FormField("Selling price per unit (£)", g, "Revenue")
        self.marketing = FormField("Marketing spend this month (£)", g, "Marketing spend")
        self.units = FormField("Units of stock to buy", g, "Stock / inventory")
        for field in (self.price, self.marketing, self.units):
            field.edit.textChanged.connect(self.update_plan)
            form.addWidget(field)
        self.hint = QLabel("")
        self.hint.setObjectName("Muted")
        self.hint.setWordWrap(True)
        form.addWidget(self.hint)
        form.addStretch()
        columns.addWidget(form_card, 3)

        # Right card: where the business stands, and what this plan costs
        panel = SoftCard()
        panel_layout = QGridLayout(panel)
        panel_layout.setContentsMargins(22, 18, 22, 20)
        panel_layout.setVerticalSpacing(10)
        panel_layout.addWidget(section("Your position"), 0, 0, 1, 2)
        self.cash_now = self._panel_row(panel_layout, 1, "Cash now", "Cash balance")
        self.stock_now = self._panel_row(panel_layout, 2, "Stock on hand", "Stock / inventory")
        self.unit_cost = self._panel_row(panel_layout, 3, "Cost to buy one unit",
                                         "Cost of goods sold (COGS)")
        self.fixed = self._panel_row(panel_layout, 4, "Fixed costs this month", "Fixed costs")
        panel_layout.addWidget(rule(), 5, 0, 1, 2)
        self.plan_cost = self._panel_row(panel_layout, 6, "This plan costs now", None)
        self.cash_left = self._panel_row(panel_layout, 7, "Cash left after purchases",
                                         "Cash flow")
        self.fixed_note = QLabel("")
        self.fixed_note.setObjectName("Muted")
        self.fixed_note.setWordWrap(True)
        panel_layout.addWidget(self.fixed_note, 8, 0, 1, 2)
        panel_layout.setRowStretch(9, 1)
        columns.addWidget(panel, 2)
        self.body.addLayout(columns)

        self.errors = QLabel("")
        self.errors.setObjectName("Error")
        self.errors.setWordWrap(True)
        self.errors.hide()
        self.body.addWidget(self.errors)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        self.simulate = QPushButton("")
        self.simulate.setObjectName("Primary")
        self.simulate.clicked.connect(self.run)
        back = QPushButton("Back to hub")
        back.clicked.connect(lambda: self.app.go("hub"))
        buttons.addWidget(self.simulate)
        buttons.addWidget(back)
        buttons.addStretch()
        self.body.addLayout(buttons)
        self.body.addStretch()
        self.business = None

    def _panel_row(self, layout, row, text, term):
        if term:
            layout.addWidget(InfoLabel(text, term, self.app.glossary), row, 0)
        else:
            layout.addWidget(QLabel(text), row, 0)
        value = QLabel("")
        layout.addWidget(value, row, 1)
        return value

    def refresh(self):
        self.business = self.app.service.get_business(self.app.business_id)
        b = self.business
        month = b.current_month + 1
        self.title.setText(f"Month {month} decisions")
        self.simulate.setText(f"Simulate month {month}")
        self.price.setText(b.price)
        self.marketing.setText(b.marketing_budget)
        self.units.setText("0")
        for field in (self.price, self.marketing, self.units):
            field.set_error("")
        self.errors.hide()
        self.cash_now.setText(fmt_money(b.cash))
        self.stock_now.setText(f"{fmt_units(b.stock)} units")
        self.unit_cost.setText(fmt_money(b.unit_cost))
        self.fixed.setText(fmt_money(b.fixed_cost))
        self.fixed_note.setText("Fixed costs are paid at the end of the month, out of "
                                "your cash and that month's sales.")
        self.hint.setText(f"The typical price in this industry is "
                          f"{fmt_money(b.reference_price)}. Pricing above it lowers demand; "
                          f"pricing below it raises demand but earns less per sale.")
        self.update_plan()

    def update_plan(self, *_signal_args):
        if self.business is None:
            return
        try:
            units = int(self.units.text().replace(",", "") or "0")
            marketing = Decimal(self.marketing.text().replace(",", "") or "0")
        except (ValueError, InvalidOperation):
            self.plan_cost.setText("—")
            self.cash_left.setText("—")
            return
        cost = units * self.business.unit_cost + marketing
        left = self.business.cash - cost
        self.plan_cost.setText(fmt_money(cost))
        self.cash_left.setText(fmt_money(left))
        self.cash_left.setObjectName("Bad" if left < 0 else "Good")
        repolish(self.cash_left)

    def run(self):
        # Field-by-field messages first, so the user sees which box to fix.
        _, price_error = validation.parse_money(self.price.text(), "Price",
                                                maximum=validation.MAX_PRICE)
        _, marketing_error = validation.parse_money(self.marketing.text(),
                                                    "Marketing spend", allow_zero=True,
                                                    maximum=validation.MAX_CAPITAL)
        _, units_error = validation.parse_whole(self.units.text(), "Units to buy", 0,
                                                validation.MAX_UNITS)
        self.price.set_error(price_error)
        self.marketing.set_error(marketing_error)
        self.units.set_error(units_error)

        decisions, errors = self.app.service.check_decisions(
            self.app.business_id, self.price.text(), self.marketing.text(),
            self.units.text())
        if decisions is None:
            field_errors = {price_error, marketing_error, units_error}
            remaining = [e for e in errors if e not in field_errors]
            self.errors.setText("\n".join(remaining))
            self.errors.setVisible(bool(remaining))
            return
        self.errors.hide()
        report = self.app.service.run_month(self.app.business_id, decisions)
        self.app.show_results(report, from_history=False)
