"""Main window: the navigation bar and a stack holding every screen."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QButtonGroup, QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QStackedWidget, QVBoxLayout, QWidget)

from ui import soft, theme
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
    def __init__(self, service, settings=None):
        """`settings` is a QSettings used to remember the theme. Tests pass None,
        so they never change the real user's choice."""
        super().__init__()
        self.setWindowTitle("Business Startup Simulator")
        self.setMinimumSize(1000, 680)
        self.service = service
        self.settings = settings
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

        # Soft drop shadows on every button on the screens (not the nav bar).
        for screen in self.screens.values():
            for button in screen.findChildren(QPushButton):
                soft.add_button_shadow(button)
        # Buttons take focus from the Tab key only, so the focus ring shows for
        # keyboard users but doesn't stay on a button after a mouse click.
        for button in self.findChildren(QPushButton):
            button.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self.theme_switch.set_on_without_animation(theme.current().name == "dark")
        self.go("profile")

    def _build_nav(self):
        nav = QWidget()
        nav.setObjectName("NavBar")
        nav.setFixedHeight(58)
        row = QHBoxLayout(nav)
        row.setContentsMargins(22, 0, 22, 0)
        row.setSpacing(6)
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
        row.addSpacing(12)

        theme_label = QLabel("Dark mode")
        theme_label.setObjectName("ThemeLabel")
        row.addWidget(theme_label)
        self.theme_switch = soft.ToggleSwitch("Dark mode")
        self.theme_switch.toggled.connect(
            lambda on: self.set_theme("dark" if on else "light"))
        row.addWidget(self.theme_switch)
        row.addSpacing(12)

        switch_profile = QPushButton("Switch profile")
        switch_profile.clicked.connect(lambda: self.go("profile"))
        row.addWidget(switch_profile)
        return nav

    # ---- theme ----------------------------------------------------------
    def set_theme(self, name):
        """Re-colour the whole app, then let screens with hand-drawn colours redraw."""
        soft.apply_theme(QApplication.instance(), name)
        for screen in self.screens.values():
            screen.retheme()
            for button in screen.findChildren(QPushButton):
                soft.recolour_button_shadow(button)
        soft.set_dark_title_bar(self, name == "dark")
        if self.theme_switch.isChecked() != (name == "dark"):
            self.theme_switch.set_on_without_animation(name == "dark")
        if self.settings is not None:
            self.settings.setValue("theme", name)

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
        # Start keyboard focus on the new page, not on whatever was clicked.
        screen.setFocus()

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
