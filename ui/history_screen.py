"""History: every simulated month, sortable (merge sort) and searchable (binary search)."""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QAbstractItemView, QComboBox, QHBoxLayout, QHeaderView,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem)

from logic.models import MonthReport
from ui import theme
from ui.style import fmt_money, fmt_units
from ui.widgets import Screen, card

RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

# Column heading, MonthResult field, how to show it
COLUMNS = [
    ("Month", "month_no", str),
    ("Price", "price", fmt_money),
    ("Marketing", "marketing_spend", fmt_money),
    ("Bought", "units_purchased", fmt_units),
    ("Demand", "demand", fmt_units),
    ("Sold", "units_sold", fmt_units),
    ("Closing stock", "closing_stock", fmt_units),
    ("Revenue", "revenue", fmt_money),
    ("Total costs", "total_costs", fmt_money),
    ("Profit", "profit", fmt_money),
    ("Closing cash", "closing_cash", fmt_money),
]

SORT_OPTIONS = [
    ("Month", "month_no"), ("Profit", "profit"), ("Revenue", "revenue"),
    ("Total costs", "total_costs"), ("Closing cash", "closing_cash"),
    ("Demand", "demand"), ("Closing stock", "closing_stock"),
]


class HistoryScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "History",
                         "Every month you've simulated. Sort by any figure to find your "
                         "best and worst months, or jump straight to one month.",
                         max_width=1400)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        controls.addWidget(QLabel("Sort by"))
        self.sort_key = QComboBox()
        self.sort_key.setAccessibleName("Sort by")
        for text, key in SORT_OPTIONS:
            self.sort_key.addItem(text, key)
        self.order = QComboBox()
        self.order.setAccessibleName("Order")
        self.order.addItem("Highest first", True)
        self.order.addItem("Lowest first", False)
        sort_button = QPushButton("Sort")
        sort_button.clicked.connect(self.sort)
        controls.addWidget(self.sort_key)
        controls.addWidget(self.order)
        controls.addWidget(sort_button)
        controls.addSpacing(24)
        controls.addWidget(QLabel("Go to month"))
        self.month_box = QLineEdit()
        self.month_box.setAccessibleName("Go to month")
        self.month_box.setMaximumWidth(90)
        self.month_box.returnPressed.connect(self.find_month)
        find_button = QPushButton("Find")
        find_button.clicked.connect(self.find_month)
        controls.addWidget(self.month_box)
        controls.addWidget(find_button)
        controls.addStretch()
        self.body.addLayout(controls)

        self.message = QLabel("")
        self.message.setObjectName("Error")
        self.message.hide()
        self.body.addWidget(self.message)

        table_card, table_layout = card(margins=(14, 10, 14, 12))
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels([c[0] for c in COLUMNS])
        # Column widths are set by fit_columns(), so no figure is cut off (DL-2).
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setDefaultAlignment(RIGHT)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(38)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(False)   # sorting is done by our merge sort
        self.table.setMinimumHeight(340)
        self.table.cellDoubleClicked.connect(lambda _r, _c: self.view_statement())
        table_layout.addWidget(self.table)
        self.empty = QLabel("No months yet. Simulate your first month from the "
                            "business hub.")
        self.empty.setObjectName("Muted")
        table_layout.addWidget(self.empty)
        self.body.addWidget(table_card)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        view = QPushButton("View month statement")
        view.setObjectName("Primary")
        view.clicked.connect(self.view_statement)
        back = QPushButton("Back to hub")
        back.clicked.connect(lambda: self.app.go("hub"))
        buttons.addWidget(view)
        buttons.addWidget(back)
        buttons.addStretch()
        self.body.addLayout(buttons)
        self.body.addStretch()
        self.rows = []

    def refresh(self):
        business = self.app.service.get_business(self.app.business_id)
        self.title.setText(f"{business.name}: history")
        self.message.hide()
        self.month_box.clear()
        self.sort_key.setCurrentIndex(0)
        self.order.setCurrentIndex(1)
        self.show_rows(self.app.service.history(self.app.business_id))

    def retheme(self):
        # Loss figures are coloured cell by cell, so colour them again.
        self.show_rows(self.rows)

    def show_rows(self, rows):
        self.rows = rows
        loss_colour = QColor(theme.current().bad)
        self.table.setRowCount(len(rows))
        for r, record in enumerate(rows):
            for c, (_, field, fmt) in enumerate(COLUMNS):
                value = getattr(record, field)
                item = QTableWidgetItem(fmt(value))
                item.setTextAlignment(RIGHT)
                if field == "profit" and value < 0:
                    item.setForeground(loss_colour)
                self.table.setItem(r, c, item)
        self.empty.setVisible(not rows)
        self.fit_columns()

    def fit_columns(self):
        """Make every column as wide as its widest entry, then share any spare
        width between them, so figures are never cut off (DL-2)."""
        self.table.resizeColumnsToContents()
        spare = self.table.viewport().width() - self.table.horizontalHeader().length()
        if spare > 0:
            extra = spare // self.table.columnCount()
            for col in range(self.table.columnCount()):
                self.table.setColumnWidth(col, self.table.columnWidth(col) + extra)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_columns()

    def sort(self):
        self.message.hide()
        ordered = self.app.service.sorted_history(self.app.business_id,
                                                  self.sort_key.currentData(),
                                                  self.order.currentData())
        self.show_rows(ordered)

    def find_month(self):
        record, error = self.app.service.find_month(self.app.business_id,
                                                    self.month_box.text())
        if error:
            self.message.setText(error)
            self.message.show()
            return
        self.message.hide()
        # Show the table in month order again, then highlight the month found.
        self.refresh_order_only()
        for row, shown in enumerate(self.rows):
            if shown.month_no == record.month_no:
                self.table.selectRow(row)
                self.table.scrollToItem(self.table.item(row, 0))
                break

    def refresh_order_only(self):
        self.sort_key.setCurrentIndex(0)
        self.order.setCurrentIndex(1)
        self.show_rows(self.app.service.history(self.app.business_id))

    def view_statement(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.rows):
            self.message.setText("Select a month to view its statement.")
            self.message.show()
            return
        self.app.show_results(MonthReport(self.rows[row], []), from_history=True)
