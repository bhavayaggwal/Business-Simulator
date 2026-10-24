"""Business hub: where the business stands, and the way into every business screen."""
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton

from ui.style import fmt_money, fmt_units
from ui.widgets import Screen, Tile, card, muted, section


class HubScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Business")
        g = app.glossary

        tiles = QGridLayout()
        tiles.setSpacing(2)
        self.cash = Tile("Cash balance", "Cash balance", g)
        self.stock = Tile("Stock on hand", "Stock / inventory", g)
        self.profit = Tile("Last month's profit", "Profit / loss", g)
        self.revenue = Tile("Last month's revenue", "Revenue", g)
        tiles.addWidget(self.cash, 0, 0)
        tiles.addWidget(self.stock, 0, 1)
        tiles.addWidget(self.profit, 0, 2)
        tiles.addWidget(self.revenue, 0, 3)
        self.body.addLayout(tiles)

        self.last_month = muted("")
        self.body.addWidget(self.last_month)

        self.body.addSpacing(8)
        self.body.addWidget(section("What next?"))
        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        self.decide = QPushButton("")
        self.decide.setObjectName("Primary")
        self.decide.clicked.connect(lambda: self.app.go("decisions"))
        history = QPushButton("View history")
        history.clicked.connect(lambda: self.app.go("history"))
        graphs = QPushButton("View graphs")
        graphs.clicked.connect(lambda: self.app.go("graphs"))
        buttons.addWidget(self.decide)
        buttons.addWidget(history)
        buttons.addWidget(graphs)
        buttons.addStretch()
        self.body.addLayout(buttons)

        self.body.addSpacing(12)
        set_up, set_up_layout = card(margins=(20, 14, 20, 16), spacing=6)
        set_up_layout.addWidget(section("How this business was set up"))
        self.starting = QLabel("")
        self.starting.setObjectName("Muted")
        self.starting.setWordWrap(True)
        set_up_layout.addWidget(self.starting)
        self.body.addWidget(set_up)
        self.body.addStretch()

    def refresh(self):
        service = self.app.service
        business = service.get_business(self.app.business_id)
        industry = service.get_industry(business.industry_id)
        history = service.history(business.business_id)

        self.title.setText(business.name)
        months = business.current_month
        self.subtitle.setText(f"{industry.name}, {months} month"
                              f"{'' if months == 1 else 's'} simulated")
        self.cash.set_value(fmt_money(business.cash), "bad" if business.cash < 0 else None)
        self.stock.set_value(f"{fmt_units(business.stock)} units")
        self.decide.setText(f"Make month {months + 1} decisions")

        if history:
            last = history[-1]
            self.profit.set_value(fmt_money(last.profit),
                                  "good" if last.profit >= 0 else "bad")
            self.revenue.set_value(fmt_money(last.revenue))
            self.last_month.setText(
                f"In month {last.month_no} customers wanted {fmt_units(last.demand)} units "
                f"and you sold {fmt_units(last.units_sold)} at {fmt_money(last.price)} each.")
        else:
            self.profit.set_value("—")
            self.revenue.set_value("—")
            self.last_month.setText("No months simulated yet. Start by making your first "
                                    "month's decisions.")

        self.starting.setText(
            f"Started with {fmt_money(business.starting_capital)}. Typical price in this "
            f"industry {fmt_money(business.reference_price)}; each unit costs "
            f"{fmt_money(business.unit_cost)} to buy; fixed costs "
            f"{fmt_money(business.fixed_cost)} a month.")
