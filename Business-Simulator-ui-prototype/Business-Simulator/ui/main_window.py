"""Main window: the navigation bar and a stack holding every screen."""
from PyQt6.QtWidgets import (QButtonGroup, QHBoxLayout, QLabel, QMainWindow, QPushButton,
                             QStackedWidget, QVBoxLayout, QWidget)

from ui.create_business_screen import CreateBusinessScreen
from ui.dashboard_screen import DashboardScreen
from ui.decisions_screen import DecisionsScreen
from ui.graphs_screen import GraphsScreen
from ui.help_screen import HelpScreen
from ui.history_screen import HistoryScreen
from ui.hub_screen import HubScreen
from ui.profile_screen import ProfileScreen
from ui.results_screen import ResultsScreen

BUSINESS_SCREENS = {"hub", "decisions", "results", "history", "graphs"}


class MainWindow(QMainWindow):
    def __init__(self, service):
        super().__init__()
        self.setWindowTitle("Business Startup Simulator")
        self.service = service
        self.glossary = service.glossary()
        self.user = None
        self.business_id = None
        self.last_report = None
        self.viewing_past = False

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_nav())

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        self.setCentralWidget(central)

        self.screens = {
            "profile": ProfileScreen(self),
            "dashboard": DashboardScreen(self),
            "create": CreateBusinessScreen(self),
            "hub": HubScreen(self),
            "decisions": DecisionsScreen(self),
            "results": ResultsScreen(self),
            "history": HistoryScreen(self),
            "graphs": GraphsScreen(self),
            "help": HelpScreen(self),
        }
        for screen in self.screens.values():
            self.stack.addWidget(screen)
        self.go("profile")

    def _build_nav(self):
        nav = QWidget()
        nav.setObjectName("NavBar")
        nav.setFixedHeight(52)
        row = QHBoxLayout(nav)
        row.setContentsMargins(20, 0, 20, 0)
        name = QLabel("Business Simulator")
        name.setObjectName("AppName")
        row.addWidget(name)
        row.addSpacing(24)

        self.nav_group = QButtonGroup(self)
        self.nav_buttons = {}
        for key, text in (("dashboard", "Your businesses"), ("hub", "Business hub"),
                          ("help", "Help")):
            button = QPushButton(text)
            button.setCheckable(True)
            button.clicked.connect(lambda _checked, k=key: self.go(k))
            self.nav_group.addButton(button)
            self.nav_buttons[key] = button
            row.addWidget(button)
        row.addStretch()

        self.who = QLabel("")
        self.who.setObjectName("WhoAmI")
        row.addWidget(self.who)
        switch = QPushButton("Switch profile")
        switch.clicked.connect(lambda: self.go("profile"))
        row.addWidget(switch)
        return nav

    # ---- navigation -----------------------------------------------------
    def go(self, name):
        if name in BUSINESS_SCREENS and self.business_id is None:
            name = "dashboard" if self.user else "profile"
        if name in ("dashboard", "create") and self.user is None:
            name = "profile"
        screen = self.screens[name]
        screen.refresh()
        self.stack.setCurrentWidget(screen)
        self._update_nav(name)

    def _update_nav(self, current):
        self.nav_buttons["dashboard"].setEnabled(self.user is not None)
        self.nav_buttons["hub"].setEnabled(self.business_id is not None)
        highlight = "hub" if current in BUSINESS_SCREENS else current
        self.nav_group.setExclusive(False)
        for key, button in self.nav_buttons.items():
            button.setChecked(key == highlight)
        self.nav_group.setExclusive(True)
        self.who.setText(f"Signed in as {self.user.username}" if self.user else "")

    def sign_in(self, profile):
        self.user = profile
        self.business_id = None
        self.last_report = None
        self.go("dashboard")

    def open_business(self, business_id):
        self.business_id = business_id
        self.last_report = None
        self.go("hub")

    def show_results(self, report, from_history):
        self.last_report = report
        self.viewing_past = from_history
        self.go("results")
