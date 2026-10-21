"""Dashboard: this profile's businesses, with search by name or industry."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QAbstractItemView, QComboBox, QHBoxLayout, QHeaderView,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem)

from ui.style import fmt_money
from ui.widgets import Screen


class DashboardScreen(Screen):
    COLUMNS = ["Business", "Industry", "Months simulated", "Cash balance"]

    def __init__(self, app):
        super().__init__(app, "Your businesses")

        # Search row (linear search, objective 11)
        search_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search your businesses")
        self.search_box.returnPressed.connect(self.search)
        self.search_field = QComboBox()
        self.search_field.addItem("by name", "name")
        self.search_field.addItem("by industry", "industry_name")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        show_all = QPushButton("Show all")
        show_all.clicked.connect(self.show_all)
        search_row.addWidget(self.search_box, 1)
        search_row.addWidget(self.search_field)
        search_row.addWidget(search_button)
        search_row.addWidget(show_all)
        self.body.addLayout(search_row)

        self.message = QLabel("")
        self.message.setObjectName("Error")
        self.message.hide()
        self.body.addWidget(self.message)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setMinimumHeight(260)
        self.table.cellDoubleClicked.connect(lambda _r, _c: self.open_selected())
        self.body.addWidget(self.table)

        self.empty = QLabel("")
        self.empty.setObjectName("Muted")
        self.empty.hide()
        self.body.addWidget(self.empty)

        buttons = QHBoxLayout()
        open_button = QPushButton("Open business")
        open_button.setObjectName("Primary")
        open_button.clicked.connect(self.open_selected)
        new_button = QPushButton("New business")
        new_button.clicked.connect(lambda: self.app.go("create"))
        buttons.addWidget(open_button)
        buttons.addWidget(new_button)
        buttons.addStretch()
        self.body.addLayout(buttons)
        self.body.addStretch()

    def refresh(self):
        self.subtitle.setText(f"Signed in as {self.app.user.username}. "
                              "Open a business to carry on, or start a new one.")
        self.search_box.clear()
        self.show_all()

    def show_all(self):
        self.message.hide()
        businesses = self.app.service.list_businesses(self.app.user.user_id)
        self.fill(businesses, "No businesses yet. Choose New business to set up your "
                              "first startup.")

    def search(self):
        term = self.search_box.text().strip()
        if not term:
            self.message.setText("Enter a name or industry to search for.")
            self.message.show()
            return
        self.message.hide()
        found = self.app.service.search_businesses(self.app.user.user_id,
                                                   self.search_field.currentData(), term)
        self.fill(found, f"No matching businesses for “{term}”.")

    def fill(self, businesses, empty_text):
        self.table.setRowCount(len(businesses))
        for row, b in enumerate(businesses):
            values = [b.name, b.industry_name, str(b.current_month), fmt_money(b.cash)]
            for col, text in enumerate(values):
                item = QTableWidgetItem(text)
                if col >= 2:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight
                                          | Qt.AlignmentFlag.AlignVCenter)
                if col == 0:
                    item.setData(Qt.ItemDataRole.UserRole, b.business_id)
                self.table.setItem(row, col, item)
        self.empty.setText(empty_text)
        self.empty.setVisible(not businesses)
        if businesses:
            self.table.selectRow(0)

    def open_selected(self):
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None:
            self.message.setText("Select a business to open.")
            self.message.show()
            return
        self.app.open_business(self.table.item(row, 0).data(Qt.ItemDataRole.UserRole))
