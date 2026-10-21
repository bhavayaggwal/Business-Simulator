"""Small reusable widgets shared by every screen."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
                             QVBoxLayout, QWidget)

from ui.style import MUTED


def tooltip_html(term):
    """Info-box text for one GlossaryTerm (rich text so it wraps)."""
    if term is None:
        return ""
    example = f"<br><span style='color:{MUTED}'>Example: {term.example}</span>" \
        if term.example else ""
    return (f"<qt><b>{term.term}</b><br>{term.definition}{example}</qt>")


class InfoLabel(QWidget):
    """A label with an ⓘ marker. Hovering either shows the glossary definition."""

    def __init__(self, text, term_name, glossary, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.label = QLabel(text)
        self.mark = QLabel("ⓘ")
        self.mark.setObjectName("InfoMark")
        self.mark.setCursor(Qt.CursorShape.WhatsThisCursor)
        tip = tooltip_html(glossary.get(term_name))
        self.label.setToolTip(tip)
        self.mark.setToolTip(tip)
        layout.addWidget(self.label)
        layout.addWidget(self.mark)
        layout.addStretch()

    def setText(self, text):
        self.label.setText(text)


class Screen(QWidget):
    """Base class: a scrolling page with a title, subtitle and a body layout."""

    def __init__(self, app, title, subtitle=""):
        super().__init__()
        self.app = app
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        holder = QWidget()
        row = QHBoxLayout(holder)
        row.setContentsMargins(0, 0, 0, 0)
        self.content = QWidget()
        self.content.setMaximumWidth(1000)
        row.addWidget(self.content)
        row.addStretch()
        scroll.setWidget(holder)

        self.body = QVBoxLayout(self.content)
        self.body.setContentsMargins(36, 28, 36, 36)
        self.body.setSpacing(12)

        self.title = QLabel(title)
        self.title.setObjectName("Title")
        self.subtitle = QLabel(subtitle)
        self.subtitle.setObjectName("Subtitle")
        self.subtitle.setWordWrap(True)
        self.body.addWidget(self.title)
        self.body.addWidget(self.subtitle)
        self.body.addSpacing(8)

    def refresh(self):
        """Called every time the screen is shown. Screens override this."""


def section(text):
    label = QLabel(text)
    label.setObjectName("Section")
    return label


def muted(text):
    label = QLabel(text)
    label.setObjectName("Muted")
    label.setWordWrap(True)
    return label


def rule():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("color: #D5DCCF;")
    return line


class FormField(QWidget):
    """Label (optionally with an info box), text box and an error line."""

    def __init__(self, text, glossary=None, term=None, placeholder=""):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        if term and glossary is not None:
            layout.addWidget(InfoLabel(text, term, glossary))
        else:
            layout.addWidget(QLabel(text))
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        layout.addWidget(self.edit)
        self.error = QLabel("")
        self.error.setObjectName("Error")
        self.error.setWordWrap(True)
        self.error.hide()
        layout.addWidget(self.error)

    def text(self):
        return self.edit.text()

    def setText(self, value):
        self.edit.setText(str(value))

    def set_error(self, message):
        self.error.setText(message or "")
        self.error.setVisible(bool(message))
        self.edit.setProperty("invalid", bool(message))
        self.edit.style().unpolish(self.edit)
        self.edit.style().polish(self.edit)


class Tile(QFrame):
    """A headline figure: caption with an info box, and a large value."""

    def __init__(self, caption, term, glossary):
        super().__init__()
        self.setObjectName("Panel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.addWidget(InfoLabel(caption, term, glossary) if term else QLabel(caption))
        self.value = QLabel("—")
        self.value.setObjectName("TileValue")
        layout.addWidget(self.value)

    def set_value(self, text, tone=None):
        self.value.setText(text)
        colour = {"good": "#2F6B4F", "bad": "#A63D32"}.get(tone, "#1E2B3A")
        self.value.setStyleSheet(f"color: {colour};")
