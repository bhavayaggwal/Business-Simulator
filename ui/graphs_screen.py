"""Graphs: trends over time, where the money went, and revenue against costs.

matplotlib draws the charts itself, so it doesn't read the Qt style sheet.
Every colour is taken from the current theme when a chart is drawn, and the
chart is redrawn when the theme changes.
"""
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton

from ui import theme
from ui.widgets import Screen, card

matplotlib.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]

CHARTS = [
    ("Revenue, profit and cash over time", "trend"),
    ("Where the money went", "costs"),
    ("Revenue against costs each month", "bars"),
]

POUNDS = FuncFormatter(lambda v, _pos: f"−£{abs(v):,.0f}" if v < 0 else f"£{v:,.0f}")


class GraphsScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Graphs", max_width=1200)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        controls.addWidget(QLabel("Show"))
        self.chart = QComboBox()
        self.chart.setAccessibleName("Chart")
        for text, key in CHARTS:
            self.chart.addItem(text, key)
        self.chart.currentIndexChanged.connect(self.draw)
        controls.addWidget(self.chart)
        controls.addSpacing(16)
        self.compare_label = QLabel("Compare profit with")
        controls.addWidget(self.compare_label)
        self.compare = QComboBox()
        self.compare.setAccessibleName("Compare profit with")
        self.compare.currentIndexChanged.connect(self.draw)
        controls.addWidget(self.compare)
        controls.addStretch()
        self.body.addLayout(controls)

        chart_card, chart_layout = card(margins=(16, 14, 16, 14))
        self.figure = Figure(figsize=(9, 4.8))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumHeight(430)
        chart_layout.addWidget(self.canvas)
        self.body.addWidget(chart_card)

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

    def retheme(self):
        self.draw()

    # ---- drawing --------------------------------------------------------
    def _axes(self, t):
        self.figure.clear()
        self.figure.set_facecolor(t.page)
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(t.page)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(t.muted)
        ax.tick_params(colors=t.text, labelsize=9)
        ax.grid(axis="y", color=t.rule, linewidth=0.8)
        ax.set_axisbelow(True)
        return ax

    def _legend(self, ax, t):
        legend = ax.legend(frameon=False)
        for text in legend.get_texts():
            text.set_color(t.text)

    def draw(self, *_signal_args):
        if self.app.business_id is None:
            return
        t = theme.current()
        history = self.app.service.history(self.app.business_id)
        kind = self.chart.currentData()
        comparing = kind == "trend"
        self.compare_label.setVisible(comparing)
        self.compare.setVisible(comparing)

        ax = self._axes(t)
        if not history:
            ax.text(0.5, 0.5, "Simulate a month to see graphs.", ha="center",
                    va="center", color=t.muted, transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.caption.setText("")
            self.canvas.draw()
            return

        if kind == "trend":
            self.draw_trend(ax, history, t)
        elif kind == "costs":
            self.draw_costs(ax, history, t)
        else:
            self.draw_bars(ax, history, t)
        self.figure.tight_layout()
        self.canvas.draw()

    def draw_trend(self, ax, history, t):
        months = [r.month_no for r in history]
        other_id = self.compare.currentData()
        if other_id is None:
            ax.plot(months, [float(r.revenue) for r in history], color=t.accent,
                    marker="o", linewidth=2, label="Revenue")
            ax.plot(months, [float(r.profit) for r in history], color=t.text, marker="o",
                    linewidth=2, label="Profit")
            ax.plot(months, [float(r.closing_cash) for r in history], color=t.chart_third,
                    marker="o", linewidth=2, label="Closing cash")
            self.caption.setText("Revenue and profit can rise while cash falls: look for "
                                 "months where the cash line dips but profit doesn't.")
        else:
            this = self.app.service.get_business(self.app.business_id)
            other = self.app.service.get_business(other_id)
            other_history = self.app.service.history(other_id)
            ax.plot(months, [float(r.profit) for r in history], color=t.text, marker="o",
                    linewidth=2, label=this.name)
            ax.plot([r.month_no for r in other_history],
                    [float(r.profit) for r in other_history], color=t.chart_third,
                    marker="o", linewidth=2, linestyle="--", label=other.name)
            self.caption.setText("Profit by month for both businesses. Different prices "
                                 "and stock decisions show up as different shapes.")
        ax.axhline(0, color=t.muted, linewidth=0.8)
        ax.set_xlabel("Month", color=t.text)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(POUNDS)
        self._legend(ax, t)

    def draw_costs(self, ax, history, t):
        cogs = sum(float(r.cogs) for r in history)
        marketing = sum(float(r.marketing_spend) for r in history)
        fixed = sum(float(r.fixed_cost) for r in history)
        parts = [(cogs, "Cost of goods sold", t.accent),
                 (marketing, "Marketing", t.chart_third),
                 (fixed, "Fixed costs", t.muted)]
        parts = [p for p in parts if p[0] > 0]
        total = sum(p[0] for p in parts)
        ax.grid(False)
        ax.pie([p[0] for p in parts],
               labels=[f"{p[1]}\n£{p[0]:,.0f}" for p in parts],
               colors=[p[2] for p in parts], startangle=90, counterclock=False,
               autopct=lambda pct: f"{pct:.0f}%", pctdistance=0.72,
               wedgeprops={"edgecolor": t.page, "linewidth": 3},
               textprops={"color": t.text, "fontsize": 9.5})
        for text in ax.texts:
            if text.get_text().endswith("%"):
                text.set_color(t.page)
                text.set_fontweight("bold")
        ax.set_aspect("equal")
        self.caption.setText(f"All costs across {len(history)} months: £{total:,.0f}. "
                             "Fixed costs are paid every month whatever you sell.")

    def draw_bars(self, ax, history, t):
        months = [r.month_no for r in history]
        width = 0.38
        ax.bar([m - width / 2 for m in months], [float(r.revenue) for r in history],
               width, color=t.accent, label="Revenue")
        ax.bar([m + width / 2 for m in months], [float(r.total_costs) for r in history],
               width, color=t.muted, label="Total costs")
        for r in history:
            if r.profit < 0:
                ax.annotate("loss", (r.month_no, float(r.total_costs)),
                            textcoords="offset points", xytext=(0, 4), ha="center",
                            color=t.bad, fontsize=8.5)
        ax.set_xlabel("Month", color=t.text)
        ax.set_xticks(months)
        ax.yaxis.set_major_formatter(POUNDS)
        self._legend(ax, t)
        self.caption.setText("Where the green bar is taller than the grey one, the month "
                             "made a profit.")
