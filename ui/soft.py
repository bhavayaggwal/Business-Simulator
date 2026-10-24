"""Soft UI drawing: raised cards, button shadows, the theme switch.

Qt style sheets can round corners but have no box-shadow, and Qt's built-in
shadow effect only casts ONE shadow per widget. Soft UI needs two (a light
one top-left, a dark one bottom-right), so SoftCard paints its own:

    each shadow = many rounded rectangles, each a pixel bigger and almost
    transparent, drawn on top of each other. Where they overlap most (near
    the card) the shadow is darkest; it fades out towards the edge, which
    looks like a blur without the cost of a real one.
"""
import ctypes
import sys
from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPalette, QPen, QPixmap
from PyQt6.QtWidgets import QAbstractButton, QFrame, QGraphicsDropShadowEffect

from ui import theme

ASSETS_FOLDER = Path(__file__).resolve().parent / "assets"


# ---- applying a theme ----------------------------------------------------
def apply_theme(app, name):
    """Switch the whole application to a theme: palette, then style sheet."""
    t = theme.set_current(name)
    app.setPalette(_palette(t))
    app.setStyleSheet(theme.stylesheet(t, str(ASSETS_FOLDER)))
    return t


def _palette(t):
    """Colours for the parts of Qt that don't read the style sheet
    (placeholder text, pop-up menus, message boxes)."""
    palette = QPalette()
    roles = {
        QPalette.ColorRole.Window: t.page, QPalette.ColorRole.WindowText: t.text,
        QPalette.ColorRole.Base: t.well, QPalette.ColorRole.AlternateBase: t.page,
        QPalette.ColorRole.Text: t.text, QPalette.ColorRole.Button: t.page,
        QPalette.ColorRole.ButtonText: t.text, QPalette.ColorRole.Highlight: t.accent_soft,
        QPalette.ColorRole.HighlightedText: t.text, QPalette.ColorRole.ToolTipBase: t.page,
        QPalette.ColorRole.ToolTipText: t.text, QPalette.ColorRole.PlaceholderText: t.muted,
        QPalette.ColorRole.Link: t.accent,
    }
    for role, colour in roles.items():
        palette.setColor(role, QColor(colour))
    for role in (QPalette.ColorRole.Text, QPalette.ColorRole.WindowText,
                 QPalette.ColorRole.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(t.faint))
    return palette


def set_dark_title_bar(window, dark):
    """Ask Windows 10/11 to draw the window's title bar dark too. Anywhere
    else (or on older Windows) this quietly does nothing."""
    if sys.platform != "win32":
        return
    try:
        use_dark = ctypes.c_int(1 if dark else 0)
        dwm_use_immersive_dark_mode = 20
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            int(window.winId()), dwm_use_immersive_dark_mode,
            ctypes.byref(use_dark), ctypes.sizeof(use_dark))
    except (AttributeError, OSError):
        pass


# ---- shadows -------------------------------------------------------------
def _paint_shadow(painter, face, radius, offset, colour, strength, spread):
    """A soft shadow behind `face`, moved by `offset` pixels.

    Outer layers are fainter than inner ones, so the overlap builds up a smooth
    fade from the card edge outwards instead of visible steps."""
    painter.setPen(Qt.PenStyle.NoPen)
    shadow = face.translated(offset, offset)
    for grow in range(spread, 0, -1):
        layer = QColor(colour)
        layer.setAlphaF(strength * 0.22 * (1 - grow / (spread + 1)))
        painter.setBrush(layer)
        painter.drawRoundedRect(shadow.adjusted(-grow, -grow, grow, grow),
                                radius + grow, radius + grow)


class SoftCard(QFrame):
    """A panel raised out of the page. Lay widgets out on it as usual:

        card = SoftCard()
        layout = QVBoxLayout(card)

    It keeps a margin round its face for the shadows to show in.
    """

    SHADOW_ROOM = 20     # pixels round the face kept clear for the shadows
    OFFSET = 5           # how far each shadow is pushed from the face
    SPREAD = 14          # how far each shadow fades out (OFFSET + SPREAD <= ROOM)

    def __init__(self, tone="raised", radius=18):
        super().__init__()
        self.tone = tone            # "raised" (page colour) or "accent" (tinted)
        self.radius = radius
        room = self.SHADOW_ROOM
        self.setContentsMargins(room, room, room, room)
        self._cached_key = None
        self._cached_picture = None

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._picture())

    def _picture(self):
        """The card drawn once and reused until its size or the theme changes."""
        t = theme.current()
        ratio = self.devicePixelRatioF()
        key = (self.width(), self.height(), ratio, t.name, self.tone)
        if key == self._cached_key:
            return self._cached_picture

        picture = QPixmap(int(self.width() * ratio), int(self.height() * ratio))
        picture.setDevicePixelRatio(ratio)
        picture.fill(Qt.GlobalColor.transparent)
        painter = QPainter(picture)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        room = self.SHADOW_ROOM
        face = QRectF(room, room, self.width() - 2 * room, self.height() - 2 * room)
        _paint_shadow(painter, face, self.radius, self.OFFSET, t.shadow_dark,
                      t.shadow_dark_strength, self.SPREAD)
        _paint_shadow(painter, face, self.radius, -self.OFFSET, t.shadow_light,
                      t.shadow_light_strength, self.SPREAD)
        painter.setBrush(QColor(t.accent_soft if self.tone == "accent" else t.page))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(face, self.radius, self.radius)
        painter.end()

        self._cached_key = key
        self._cached_picture = picture
        return picture


def add_button_shadow(button):
    """Give a button a soft drop shadow (its highlight comes from the style sheet)."""
    effect = QGraphicsDropShadowEffect(button)
    effect.setBlurRadius(14)
    effect.setOffset(3, 3)
    button.setGraphicsEffect(effect)
    recolour_button_shadow(button)


def recolour_button_shadow(button):
    effect = button.graphicsEffect()
    if isinstance(effect, QGraphicsDropShadowEffect):
        t = theme.current()
        colour = QColor(t.shadow_dark)
        colour.setAlphaF(0.55 if t.name == "light" else 0.8)
        effect.setColor(colour)


# ---- the light/dark switch -----------------------------------------------
class ToggleSwitch(QAbstractButton):
    """An on/off switch: a sunken track with a raised knob that slides.

    It is a QAbstractButton, so it can be clicked, toggled with the Space key
    when focused, and sends the usual toggled(bool) signal.
    """

    def __init__(self, accessible_name, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setAccessibleName(accessible_name)
        self.setToolTip(accessible_name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._knob = 0.0            # 0 = off (left) ... 1 = on (right)
        self._slide = QPropertyAnimation(self, b"knob", self)
        self._slide.setDuration(160)
        self._slide.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.toggled.connect(self._start_slide)

    def sizeHint(self):
        return QSize(50, 28)

    def _get_knob(self):
        return self._knob

    def _set_knob(self, value):
        self._knob = value
        self.update()

    knob = pyqtProperty(float, _get_knob, _set_knob)

    def _start_slide(self, checked):
        self._slide.stop()
        self._slide.setStartValue(self._knob)
        self._slide.setEndValue(1.0 if checked else 0.0)
        self._slide.start()

    def set_on_without_animation(self, on):
        self.blockSignals(True)
        self.setChecked(on)
        self.blockSignals(False)
        self._slide.stop()
        self._set_knob(1.0 if on else 0.0)

    def paintEvent(self, _event):
        t = theme.current()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QRectF(1.5, 1.5, self.width() - 3, self.height() - 3)
        round_end = track.height() / 2

        # Sunken track; the accent colour fades in as the knob moves right.
        painter.setPen(QPen(QColor(t.edge_dark), 1))
        painter.setBrush(QColor(t.well))
        painter.drawRoundedRect(track, round_end, round_end)
        if self._knob > 0:
            fill = QColor(t.accent)
            fill.setAlphaF(self._knob)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(fill)
            painter.drawRoundedRect(track, round_end, round_end)

        # Raised knob with a small shadow below-right.
        size = track.height() - 6
        x = track.left() + 3 + (track.width() - 6 - size) * self._knob
        knob = QRectF(x, track.top() + 3, size, size)
        shadow = QColor(t.shadow_dark)
        shadow.setAlphaF(0.6)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shadow)
        painter.drawEllipse(knob.translated(1, 1.5))
        painter.setBrush(QColor(t.raised_hi))
        painter.setPen(QPen(QColor(t.edge_dark), 1))
        painter.drawEllipse(knob)

        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(t.text if self.isChecked() else t.accent), 2))
            painter.drawRoundedRect(track, round_end, round_end)
