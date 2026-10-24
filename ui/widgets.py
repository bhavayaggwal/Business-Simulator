"""Small reusable widgets shared by every screen."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
                             QVBoxLayout, QWidget)

from ui.soft import SoftCard


def tooltip_html(term):
    """Info-box text for one GlossaryTerm (rich text so it wraps).

    No colours here: the tooltip takes them from the current theme."""
    if term is None:
        return ""
    example = f"<br><i>Example: {term.example}</i>" if term.example else ""
    return f"<qt><b>{term.term}</b><br>{term.definition}{example}</qt>"


def repolish(widget):
    """Re-apply the style sheet after changing a property it depends on."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def set_tone(label, tone):
    """Colour a figure as 'good' (profit), 'bad' (loss) or neither (None).
    The colours come from the theme's style sheet, so they follow the theme."""
    label.setProperty("tone", tone or "")
    repolish(label)


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

    def __init__(self, app, title, subtitle="", max_width=1000):
        super().__init__()
        self.app = app
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        # The page grows with the window up to max_width, then stays centred.
        holder = QWidget()
        row = QHBoxLayout(holder)
        row.setContentsMargins(0, 0, 0, 0)
        self.content = QWidget()
        self.content.setMaximumWidth(max_width)
        row.addStretch()
        row.addWidget(self.content, 100)
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
        self.body.addSpacing(4)

    def refresh(self):
        """Called every time the screen is shown. Screens override this."""

    def retheme(self):
        """Called after the theme changes. Most widgets follow the style sheet
        by themselves; screens that draw their own colours (graphs, rich text,
        coloured table cells) override this to redraw."""


def card(margins=(22, 18, 22, 20), spacing=10, tone="raised"):
    """A SoftCard with a vertical layout ready to add widgets to."""
    panel = SoftCard(tone)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return panel, layout


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
    """A thin dividing line, coloured by the theme."""
    line = QFrame()
    line.setObjectName("Rule")
    line.setFixedHeight(1)
    return line


class FormField(QWidget):
    """Label (optionally with an info box), text box and an error line."""

    def __init__(self, text, glossary=None, term=None, placeholder=""):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        if term and glossary is not None:
            layout.addWidget(InfoLabel(text, term, glossary))
        else:
            layout.addWidget(QLabel(text))
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.setAccessibleName(text)
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
        repolish(self.edit)


class Tile(SoftCard):
    """A headline figure: caption with an info box, and a large value."""

    def __init__(self, caption, term, glossary):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 16)
        layout.setSpacing(6)
        layout.addWidget(InfoLabel(caption, term, glossary) if term else QLabel(caption))
        self.value = QLabel("—")
        self.value.setObjectName("TileValue")
        layout.addWidget(self.value)

    def set_value(self, text, tone=None):
        self.value.setText(text)
        set_tone(self.value, tone)
