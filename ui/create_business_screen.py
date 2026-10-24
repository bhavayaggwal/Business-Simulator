"""Create business: name, industry, money and stock, plus editable industry values."""
from decimal import Decimal, InvalidOperation

from PyQt6.QtWidgets import QComboBox, QGridLayout, QHBoxLayout, QLabel, QPushButton

from ui.style import fmt_money
from ui.widgets import FormField, Screen, card, muted, repolish, section


class CreateBusinessScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Start a new business",
                         "Choose an industry and how much money and stock you start "
                         "with. You can change any of these later through your monthly "
                         "decisions.")
        g = app.glossary

        # Card 1: the business itself
        business_card, business_layout = card(spacing=12)
        business_layout.addWidget(section("Your business"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(10)

        self.name = FormField("Business name", placeholder="e.g. Bean There")
        grid.addWidget(self.name, 0, 0)

        industry_box = FormField("Industry")
        industry_box.edit.hide()           # reuse the label + error layout
        self.industry = QComboBox()
        self.industry.setAccessibleName("Industry")
        industry_box.layout().insertWidget(1, self.industry)
        self.industry.currentIndexChanged.connect(self.fill_industry_defaults)
        grid.addWidget(industry_box, 0, 1)

        self.capital = FormField("Starting capital (£)", g, "Cash balance", "e.g. 10000")
        self.price = FormField("Selling price per unit (£)", g, "Revenue", "e.g. 3.20")
        self.stock = FormField("Initial stock (units)", g, "Stock / inventory", "e.g. 1500")
        self.marketing = FormField("Monthly marketing budget (£)", g, "Marketing spend",
                                   "e.g. 300")
        grid.addWidget(self.capital, 1, 0)
        grid.addWidget(self.price, 1, 1)
        grid.addWidget(self.stock, 2, 0)
        grid.addWidget(self.marketing, 2, 1)
        business_layout.addLayout(grid)

        self.summary = QLabel("")
        self.summary.setObjectName("Muted")
        business_layout.addWidget(self.summary)
        self.body.addWidget(business_card)

        # Card 2: the industry figures this business will run on
        values_card, values_layout = card(spacing=12)
        values_layout.addWidget(section("Industry starting values"))
        values_layout.addWidget(muted("Filled in with typical figures for the industry you "
                                      "chose. Change them if you want to model a particular "
                                      "business."))
        values = QGridLayout()
        values.setHorizontalSpacing(24)
        values.setVerticalSpacing(10)
        self.base_demand = FormField("Monthly demand at the typical price (units)", g,
                                     "Demand")
        self.reference_price = FormField("Typical price in this industry (£)")
        self.unit_cost = FormField("Cost to buy one unit (£)", g,
                                   "Cost of goods sold (COGS)")
        self.fixed_cost = FormField("Fixed costs per month (£)", g, "Fixed costs")
        self.sensitivity = FormField("Price sensitivity")
        values.addWidget(self.base_demand, 0, 0)
        values.addWidget(self.reference_price, 0, 1)
        values.addWidget(self.unit_cost, 1, 0)
        values.addWidget(self.fixed_cost, 1, 1)
        values.addWidget(self.sensitivity, 2, 0)
        values.addWidget(muted("How strongly customers react to price, from 0.01 to 5. "
                               "Higher means a price rise loses more customers."), 2, 1)
        values_layout.addLayout(values)
        self.body.addWidget(values_card)

        for field in (self.capital, self.stock, self.unit_cost):
            field.edit.textChanged.connect(self.update_summary)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        create = QPushButton("Create business")
        create.setObjectName("Primary")
        create.clicked.connect(self.create)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(lambda: self.app.go("dashboard"))
        buttons.addWidget(create)
        buttons.addWidget(cancel)
        buttons.addStretch()
        self.body.addLayout(buttons)
        self.body.addStretch()

        self.fields = {
            "name": self.name, "starting_capital": self.capital, "price": self.price,
            "initial_stock": self.stock, "marketing_budget": self.marketing,
            "base_demand": self.base_demand, "reference_price": self.reference_price,
            "unit_cost": self.unit_cost, "fixed_cost": self.fixed_cost,
            "price_sensitivity": self.sensitivity,
        }

    def refresh(self):
        for field in self.fields.values():
            field.edit.clear()
            field.set_error("")
        self.industry.blockSignals(True)
        self.industry.clear()
        for industry in self.app.service.list_industries():
            self.industry.addItem(industry.name, industry.industry_id)
        self.industry.blockSignals(False)
        self.fill_industry_defaults()

    def fill_industry_defaults(self, *_signal_args):
        industry = self.app.service.get_industry(self.industry.currentData())
        if industry is None:
            return
        self.base_demand.setText(industry.base_demand)
        self.reference_price.setText(industry.reference_price)
        self.unit_cost.setText(industry.unit_cost)
        self.fixed_cost.setText(industry.fixed_cost)
        self.sensitivity.setText(industry.price_sensitivity)
        self.price.setText(industry.reference_price)
        self.update_summary()

    def update_summary(self, *_signal_args):
        try:
            capital = Decimal(self.capital.text().replace(",", "") or "0")
            stock = int(self.stock.text().replace(",", "") or "0")
            unit_cost = Decimal(self.unit_cost.text() or "0")
        except (InvalidOperation, ValueError):
            self.summary.setText("")
            return
        cost = stock * unit_cost
        left = capital - cost
        self.summary.setText(f"Initial stock will cost {fmt_money(cost)}, leaving "
                             f"{fmt_money(left)} in cash.")
        self.summary.setObjectName("Bad" if left < 0 else "Muted")
        repolish(self.summary)

    def create(self):
        form = {key: field.text() for key, field in self.fields.items()}
        business, errors = self.app.service.create_business(
            self.app.user.user_id, self.industry.currentData(), form)
        for key, field in self.fields.items():
            field.set_error(errors.get(key, ""))
        if business is not None:
            self.app.open_business(business.business_id)
