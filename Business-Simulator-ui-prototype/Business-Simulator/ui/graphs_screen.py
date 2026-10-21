"""Graphs: trends over time, where the money went, and revenue against costs."""
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton

from ui.style import INK, LEDGER_GREEN, LOSS_RED, MUTED, OCHRE, PAPER, RULE
from ui.widgets import Screen

CHARTS = [
    ("Revenue, profit and cash over time", "trend"),
    ("Where the money went", "costs"),
    ("Revenue against costs each month", "bars"),
]

POUNDS = FuncFormatter(lambda v, _pos: f"−£{abs(v):,.0f}" if v < 0 else f"£{v:,.0f}")


class GraphsScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Graphs")

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Show"))
        self.chart = QComboBox()
        for text, key in CHARTS:
            self.chart.addItem(text, key)
        self.chart.currentIndexChanged.connect(self.draw)
        controls.addWidget(self.chart)
        controls.addSpacing(16)
        self.compare_label = QLabel("Compare profit with")
        controls.addWidget(self.compare_label)
        self.compare = QComboBox()
        self.compare.currentIndexChanged.connect(self.draw)
        controls.addWidget(self.compare)
        controls.addStretch()
        self.body.addLayout(controls)

        self.figure = Figure(figsize=(9, 4.8), facecolor=PAPER)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumHeight(430)
        self.body.addWidget(self.canvas)

        self.caption = QLabel("")
        self.caption.setObjectName("Muted")
        self.caption.setWordWrap(True)
        self.body.addWidget(self.caption)

        back_row = QHBoxLayout()
        back = QPushButton("Back to hub")
        back.clicked.connect(lambda: self.app.go("hub"))
        back_row.addWidget(back)
        back_row.addStretch()
        self.body.addLayout(back_row)
        self.body.addStretch()

    def refresh(self):
        service = self.app.service
        business = service.get_business(self.app.business_id)
        self.title.setText(f"{business.name}: graphs")
        self.compare.blockSignals(True)
        self.compare.clear()
        self.compare.addItem("No comparison", None)
        for other in service.list_businesses(self.app.user.user_id):
            if other.business_id != business.business_id and other.current_month > 0:
                self.compare.addItem(other.name, other.business_id)
        self.compare.blockSignals(False)
        self.draw()

    # ---- drawing --------------------------------------------------------
    def _axes(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(PAPER)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(MUTED)
        ax.tick_params(colors=INK, labelsize=9)
        ax.grid(axis="y", color=RULE, linewidth=0.8)
        ax.set_axisbelow(True)
        return ax

    def draw(self, *_signal_args):
        if self.app.business_id is None:
            return
        history = self.app.service.history(self.app.business_id)
        kind = self.chart.currentData()
        comparing = kind == "trend"
        self.compare_label.setVisible(comparing)
        self.compare.setVisible(comparing)

        ax = self._axes()
        if not history:
            ax.text(0.5, 0.5, "Simulate a month to see graphs.", ha="center",
                    va="center", color=MUTED, transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.caption.setText("")
            self.canvas.draw()
            return

        if kind == "trend":
            self.draw_trend(ax, history)
        elif kind == "costs":
            self.draw_costs(ax, history)
        else:
            self.draw_bars(ax, history)
        self.figure.tight_layout()
        self.canvas.draw()

    def draw_trend(self, ax, history):
        months = [r.month_no for r in history]
        other_id = self.compare.currentData()
        if other_id is None:
            ax.plot(months, [float(r.revenue) for r in history], color=LEDGER_GREEN,
                    marker="o", linewidth=2, label="Revenue")
            ax.plot(months, [float(r.profit) for r in history], color=INK, marker="o",
                    linewidth=2, label="Profit")
            ax.plot(months, [float(r.closing_cash) for r in history], color=OCHRE,
                    marker="o", linewidth=2, label="Closing cash")
            self.caption.setText("Revenue and profit can rise while cash falls: look for "
                                 "months where the cash line dips but profit doesn't.")
        else:
            this = self.app.service.get_business(self.app.business_id)
            other = self.app.service.get_business(other_id)
            other_history = self.app.service.history(other_id)
            ax.plot(months, [float(r.profit) for r in history], color=INK, marker="o",
                    linewidth=2, label=this.name)
            ax.plot([r.month_no for r in other_history],
                    [float(r.profit) for r in other_history], color=OCHRE, marker="o",
                    linewidth=2, linestyle="--", label=other.name)
            self.caption.setText("Profit by month for both businesses. Different prices "
                                 "and stock decisions show up as different shapes.")
        ax.axhline(0, color=MUTED, linewidth=0.8)
        ax.set_xlabel("Month", color=INK)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(POUNDS)
        ax.legend(frameon=False)

    def draw_costs(self, ax, history):
        cogs = sum(float(r.cogs) for r in history)
        marketing = sum(float(r.marketing_spend) for r in history)
        fixed = sum(float(r.fixed_cost) for r in history)
        parts = [(cogs, "Cost of goods sold", LEDGER_GREEN),
                 (marketing, "Marketing", OCHRE),
                 (fixed, "Fixed costs", MUTED)]
        parts = [p for p in parts if p[0] > 0]
        total = sum(p[0] for p in parts)
        ax.grid(False)
        ax.pie([p[0] for p in parts],
               labels=[f"{p[1]}\n£{p[0]:,.0f}" for p in parts],
               colors=[p[2] for p in parts], startangle=90, counterclock=False,
               autopct=lambda pct: f"{pct:.0f}%", pctdistance=0.72,
               wedgeprops={"edgecolor": PAPER, "linewidth": 2},
               textprops={"color": INK, "fontsize": 9.5})
        for text in ax.texts:
            if text.get_text().endswith("%"):
                text.set_color("white")
        ax.set_aspect("equal")
        self.caption.setText(f"All costs across {len(history)} months: £{total:,.0f}. "
                             "Fixed costs are paid every month whatever you sell.")

    def draw_bars(self, ax, history):
        months = [r.month_no for r in history]
        width = 0.38
        ax.bar([m - width / 2 for m in months], [float(r.revenue) for r in history],
               width, color=LEDGER_GREEN, label="Revenue")
        ax.bar([m + width / 2 for m in months], [float(r.total_costs) for r in history],
               width, color=MUTED, label="Total costs")
        for r in history:
            if r.profit < 0:
                ax.annotate("loss", (r.month_no, float(r.total_costs)),
                            textcoords="offset points", xytext=(0, 4), ha="center",
                            color=LOSS_RED, fontsize=8.5)
        ax.set_xlabel("Month", color=INK)
        ax.set_xticks(months)
        ax.yaxis.set_major_formatter(POUNDS)
        ax.legend(frameon=False)
        self.caption.setText("Where the green bar is taller than the grey one, the month "
                             "made a profit.")
