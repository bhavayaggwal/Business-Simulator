"""Month results, laid out like real financial statements.

Profit and loss sits beside the cash statement so the student can see, line
by line, why profit and the change in cash are different numbers. Deductions
are shown in brackets and totals are double-underlined, as in a set of accounts.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ui import theme
from ui.soft import SoftCard
from ui.style import fmt_deduction, fmt_money, fmt_units
from ui.widgets import InfoLabel, Screen, card, rule, set_tone

RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class StatementSheet(SoftCard):
    """One statement: a heading, then label / amount lines and a total."""

    def __init__(self, heading, glossary):
        super().__init__()
        self.glossary = glossary
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(22, 16, 22, 18)
        self.grid.setHorizontalSpacing(24)
        self.grid.setVerticalSpacing(5)
        title = QLabel(heading)
        title.setObjectName("Section")
        self.grid.addWidget(title, 0, 0, 1, 2)
        self.row = 1

    def _label(self, text, term):
        if term:
            return InfoLabel(text, term, self.glossary)
        return QLabel(text)

    def line(self, text, amount, term=None):
        self.grid.addWidget(self._label(text, term), self.row, 0)
        value = QLabel(amount)
        value.setAlignment(RIGHT)
        self.grid.addWidget(value, self.row, 1)
        self.grid.addWidget(rule(), self.row + 1, 0, 1, 2)
        self.row += 2

    def total(self, text, amount, term=None, tone=None):
        self.grid.addWidget(self._label(text, term), self.row, 0)
        value = QLabel(amount)
        value.setObjectName("Total")
        value.setAlignment(RIGHT)
        set_tone(value, tone)
        self.grid.addWidget(value, self.row, 1)
        self.row += 1


class ResultsScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Month results")
        self.headline = QLabel("")
        self.headline.setWordWrap(True)
        self.headline.setTextFormat(Qt.TextFormat.RichText)
        self.body.addWidget(self.headline)

        self.sheets_area = QVBoxLayout()
        self.sheets_area.setSpacing(0)
        self.body.addLayout(self.sheets_area)

        self.explain, explain_layout = card(margins=(22, 16, 22, 18), spacing=6,
                                            tone="accent")
        explain_title = QLabel("What happened this month")
        explain_title.setObjectName("ExplainTitle")
        explain_layout.addWidget(explain_title)
        self.explain_text = QLabel("")
        self.explain_text.setWordWrap(True)
        explain_layout.addWidget(self.explain_text)
        self.body.addWidget(self.explain)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        self.next_button = QPushButton("Next month")
        self.next_button.setObjectName("Primary")
        self.next_button.clicked.connect(lambda: self.app.go("decisions"))
        self.back_button = QPushButton("Back to hub")
        self.back_button.clicked.connect(lambda: self.app.go("hub"))
        self.history_button = QPushButton("Back to history")
        self.history_button.clicked.connect(lambda: self.app.go("history"))
        buttons.addWidget(self.next_button)
        buttons.addWidget(self.history_button)
        buttons.addWidget(self.back_button)
        buttons.addStretch()
        self.body.addLayout(buttons)
        self.body.addStretch()

    def _clear_sheets(self):
        """Remove the previous month's statements.

        deleteLater() only deletes a widget once Qt is next idle, so each one is
        hidden first; otherwise it stays on screen behind the new statements."""
        while self.sheets_area.count():
            item = self.sheets_area.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()
            elif item.layout():
                inner = item.layout()
                while inner.count():
                    child = inner.takeAt(0)
                    if child.widget():
                        child.widget().hide()
                        child.widget().deleteLater()
                inner.deleteLater()

    def retheme(self):
        # The headline is rich text with colours written into it, so redraw it.
        self.refresh()

    def refresh(self):
        report = self.app.last_report
        if report is None:
            return
        r = report.result
        g = self.app.glossary
        t = theme.current()
        self.title.setText(f"Month {r.month_no} results")
        self.subtitle.setText(f"Price {fmt_money(r.price)}, marketing "
                              f"{fmt_money(r.marketing_spend)}, "
                              f"{fmt_units(r.units_purchased)} units bought.")

        cash_change = r.closing_cash - r.opening_cash
        profit_word = "a profit" if r.profit >= 0 else "a loss"
        profit_tone = "good" if r.profit >= 0 else "bad"
        cash_word = "rose" if cash_change >= 0 else "fell"
        profit_colour = t.good if r.profit >= 0 else t.bad
        cash_colour = t.good if cash_change >= 0 else t.bad
        self.headline.setText(
            f"<span style='font-size:13pt'>You made {profit_word} of "
            f"<b style='color:{profit_colour}'>{fmt_money(abs(r.profit))}</b>, and your "
            f"cash {cash_word} by <b style='color:{cash_colour}'>"
            f"{fmt_money(abs(cash_change))}</b>.</span>")

        self._clear_sheets()

        # Sales and stock
        sales = StatementSheet("Sales and stock", g)
        sales.line("Demand (units customers wanted)", fmt_units(r.demand), "Demand")
        sales.line("Units sold", fmt_units(r.units_sold), "Units sold")
        sales.line("Opening stock", fmt_units(r.opening_stock), "Stock / inventory")
        sales.line("Stock bought", fmt_units(r.units_purchased))
        sales.line("Stock sold", f"({fmt_units(r.units_sold)})")
        sales.total("Closing stock", f"{fmt_units(r.closing_stock)} units")

        # Profit and loss
        pnl = StatementSheet("Profit and loss", g)
        pnl.line("Revenue", fmt_money(r.revenue), "Revenue")
        pnl.line("Cost of goods sold", fmt_deduction(r.cogs), "Cost of goods sold (COGS)")
        pnl.line("Marketing", fmt_deduction(r.marketing_spend), "Marketing spend")
        pnl.line("Fixed costs", fmt_deduction(r.fixed_cost), "Fixed costs")
        pnl.total("Profit" if r.profit >= 0 else "Loss", fmt_money(r.profit),
                  "Profit / loss", profit_tone)

        # Cash
        cash = StatementSheet("Cash", g)
        cash.line("Opening cash", fmt_money(r.opening_cash), "Cash balance")
        cash.line("Money from sales", fmt_money(r.revenue), "Cash flow")
        cash.line("Stock bought", fmt_deduction(r.stock_purchase_cost), "Stock / inventory")
        cash.line("Marketing", fmt_deduction(r.marketing_spend))
        cash.line("Fixed costs", fmt_deduction(r.fixed_cost))
        cash.total("Closing cash", fmt_money(r.closing_cash), "Cash balance",
                   "bad" if r.closing_cash < 0 else None)

        self.sheets_area.addWidget(sales)
        side_by_side = QHBoxLayout()
        side_by_side.setSpacing(0)
        side_by_side.addWidget(pnl)
        side_by_side.addWidget(cash)
        self.sheets_area.addLayout(side_by_side)

        difference = r.stock_purchase_cost - r.cogs
        note = ""
        if difference != 0:
            more_or_less = "more" if difference > 0 else "less"
            note = (f"\n\nWhy profit and cash differ: you spent {fmt_money(abs(difference))} "
                    f"{more_or_less} on buying stock than the stock you sold cost. Stock "
                    f"is paid for when it's bought, but only counts as a cost when it's sold.")

        explanations = report.explanations
        self.explain.setVisible(bool(explanations) or bool(note))
        self.explain_text.setText("\n".join(f"• {e}" for e in explanations) + note)

        viewing_past = self.app.viewing_past
        self.next_button.setVisible(not viewing_past)
        self.history_button.setVisible(viewing_past)
