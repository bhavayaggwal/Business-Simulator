"""Profile select: choose who is using the laptop, or create a new profile."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton

from ui.widgets import FormField, Screen, card, muted, section


class ProfileScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Who's using the simulator?",
                         "Pick your profile to see your businesses. Each profile keeps its "
                         "own simulations separate, and only a username is stored.")
        columns = QHBoxLayout()
        columns.setSpacing(4)

        # Left card: existing profiles
        choose, choose_layout = card()
        choose_layout.addWidget(section("Choose your profile"))
        self.profiles = QListWidget()
        self.profiles.setMinimumHeight(200)
        self.profiles.setAccessibleName("Profiles")
        self.profiles.itemDoubleClicked.connect(lambda _item: self.continue_with_selected())
        choose_layout.addWidget(self.profiles)
        self.pick_error = QLabel("")
        self.pick_error.setObjectName("Error")
        self.pick_error.hide()
        choose_layout.addWidget(self.pick_error)
        row = QHBoxLayout()
        continue_button = QPushButton("Continue")
        continue_button.setObjectName("Primary")
        continue_button.clicked.connect(self.continue_with_selected)
        row.addWidget(continue_button)
        row.addStretch()
        choose_layout.addLayout(row)
        columns.addWidget(choose, 1)

        # Right card: a new profile
        create, create_layout = card()
        create_layout.addWidget(section("New profile"))
        create_layout.addWidget(muted("3–30 letters, numbers or underscores. "
                                      "Don't use your full name."))
        self.new_name = FormField("Username", placeholder="e.g. alex_k")
        self.new_name.edit.returnPressed.connect(self.create_profile)
        create_layout.addWidget(self.new_name)
        create_row = QHBoxLayout()
        create_button = QPushButton("Create profile")
        create_button.clicked.connect(self.create_profile)
        create_row.addWidget(create_button)
        create_row.addStretch()
        create_layout.addLayout(create_row)
        create_layout.addStretch()
        columns.addWidget(create, 1)

        self.body.addLayout(columns)
        self.body.addStretch()

    def refresh(self):
        self.pick_error.hide()
        self.new_name.set_error("")
        self.profiles.clear()
        for profile in self.app.service.list_profiles():
            item = QListWidgetItem(profile.username)
            item.setData(Qt.ItemDataRole.UserRole, profile)
            self.profiles.addItem(item)
            if self.app.user and self.app.user.user_id == profile.user_id:
                self.profiles.setCurrentItem(item)

    def continue_with_selected(self):
        item = self.profiles.currentItem()
        if item is None:
            self.pick_error.setText("Choose a profile first, or create a new one.")
            self.pick_error.show()
            return
        self.app.sign_in(item.data(Qt.ItemDataRole.UserRole))

    def create_profile(self):
        profile, error = self.app.service.create_profile(self.new_name.text())
        if error:
            self.new_name.set_error(error)
            return
        self.new_name.edit.clear()
        self.app.sign_in(profile)
