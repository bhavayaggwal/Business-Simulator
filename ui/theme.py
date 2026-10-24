"""Light and dark themes for the soft (neumorphic) design.

Colours are named by their ROLE (page, text, accent...), never by what they
look like, so swapping one Theme for another re-colours the whole app. This
module is plain Python: no Qt, so the colours can be unit tested.

Soft UI in one sentence: cards and buttons are the same colour as the page,
and look raised because of a light shadow on their top-left edge and a dark
one on their bottom-right, as if lit from the top-left.
"""
from dataclasses import dataclass

BODY_FONT = "Segoe UI"


@dataclass(frozen=True)
class Theme:
    name: str
    page: str            # background of the window, cards and buttons
    well: str            # inside text boxes and other sunken areas
    raised_hi: str       # lit (top-left) end of a raised button
    raised_lo: str       # shaded (bottom-right) end of a raised button
    text: str
    muted: str           # secondary text
    faint: str           # disabled text (decorative, so no contrast minimum)
    accent: str          # main buttons, focus rings, info marks
    accent_hi: str       # lit end of a main button
    on_accent: str       # text on an accent button
    accent_soft: str     # selected rows, the explanation card
    good: str            # profit
    bad: str             # loss and error messages
    chart_third: str     # third chart line (closing cash)
    rule: str            # thin lines between statement rows
    scrollbar: str
    shadow_dark: str     # the bottom-right shadow
    shadow_light: str    # the top-left highlight
    shadow_dark_strength: float
    shadow_light_strength: float
    edge_dark: str       # 1px edges that fake the light direction
    edge_light: str


LIGHT = Theme(
    name="light",
    page="#E6EBF1", well="#DCE2EA", raised_hi="#F0F3F7", raised_lo="#DAE0E8",
    text="#1E2A38", muted="#4F5D6D", faint="#9AA6B3",
    accent="#2E6B50", accent_hi="#367D5D", on_accent="#FFFFFF", accent_soft="#D2E2D9",
    good="#2A6649", bad="#A3392E", chart_third="#875811", rule="#CAD2DC",
    scrollbar="#B5C0CC",
    shadow_dark="#A3B1C2", shadow_light="#FFFFFF",
    shadow_dark_strength=0.75, shadow_light_strength=1.0,
    edge_dark="#C2CBD6", edge_light="#F8FAFC",
)

DARK = Theme(
    name="dark",
    page="#252A32", well="#1D2127", raised_hi="#2E343D", raised_lo="#22262D",
    text="#E7ECF2", muted="#A9B4C2", faint="#5F6976",
    accent="#5FC292", accent_hi="#78D3A8", on_accent="#0E2118", accent_soft="#2E463B",
    good="#6CD29E", bad="#FF8E7F", chart_third="#E3A548", rule="#38404B",
    scrollbar="#4A5360",
    shadow_dark="#121418", shadow_light="#353C48",
    shadow_dark_strength=0.9, shadow_light_strength=0.55,
    edge_dark="#171A1F", edge_light="#363D48",
)

THEMES = {"light": LIGHT, "dark": DARK}

_current = LIGHT


def current() -> Theme:
    return _current


def set_current(name) -> Theme:
    """Make `name` ('light' or 'dark') the theme every screen draws with."""
    global _current
    _current = THEMES.get(name, LIGHT)
    return _current


# ---- accessibility ------------------------------------------------------
def _channel(value):
    """One sRGB channel (0-255) as linear light, as WCAG defines it."""
    c = value / 255
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour) -> float:
    hex_colour = hex_colour.lstrip("#")
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(foreground, background) -> float:
    """WCAG contrast ratio, from 1 (none) to 21 (black on white).
    Normal text needs at least 4.5 to meet WCAG AA."""
    lighter = max(luminance(foreground), luminance(background))
    darker = min(luminance(foreground), luminance(background))
    return (lighter + 0.05) / (darker + 0.05)


# Every pair of colours the app uses for text: (text colour, background colour).
TEXT_PAIRS = [
    ("text", "page"), ("muted", "page"), ("text", "well"), ("muted", "well"),
    ("accent", "page"), ("good", "page"), ("bad", "page"), ("bad", "well"),
    ("on_accent", "accent"), ("on_accent", "accent_hi"), ("text", "accent_soft"),
    ("text", "raised_hi"), ("text", "raised_lo"), ("accent", "raised_lo"),
    ("chart_third", "page"),
]


# ---- the style sheet ------------------------------------------------------
def stylesheet(t: Theme, assets_folder: str) -> str:
    """Qt style sheet for one theme. `assets_folder` holds the arrow images."""
    arrow = f"{assets_folder}/chevron-{t.name}.svg".replace("\\", "/")
    sunken = (f"border-top-color: {t.edge_dark}; border-left-color: {t.edge_dark}; "
              f"border-bottom-color: {t.edge_light}; border-right-color: {t.edge_light};")
    raised = (f"border-top-color: {t.edge_light}; border-left-color: {t.edge_light}; "
              f"border-bottom-color: {t.edge_dark}; border-right-color: {t.edge_dark};")
    return f"""
QWidget {{
    font-family: "{BODY_FONT}", "Helvetica Neue", Arial;
    font-size: 10.5pt;
    color: {t.text};
}}
QMainWindow, QStackedWidget, QScrollArea, QScrollArea > QWidget > QWidget,
QDialog, QMessageBox {{
    background: {t.page};
}}
QLabel {{ background: transparent; }}

/* Navigation bar */
#NavBar {{ background: {t.page}; border-bottom: 1px solid {t.edge_dark}; }}
#NavBar QLabel#AppName {{ font-size: 13.5pt; font-weight: 700; }}
#NavBar QPushButton {{
    background: transparent; border: 1px solid transparent; border-radius: 11px;
    padding: 6px 14px; color: {t.muted}; font-weight: 600;
}}
#NavBar QPushButton:hover {{ color: {t.text}; }}
#NavBar QPushButton:checked {{
    color: {t.accent}; background: {t.well}; border: 1px solid; {sunken}
}}
#NavBar QPushButton:focus {{ border: 1px solid {t.accent}; }}
#NavBar QPushButton:disabled {{ color: {t.faint}; }}
#NavBar QLabel#WhoAmI, #NavBar QLabel#ThemeLabel {{ color: {t.muted}; font-size: 9.5pt; }}

/* Text */
QLabel#Title {{ font-size: 22pt; font-weight: 600; }}
QLabel#Subtitle {{ color: {t.muted}; font-size: 10.5pt; }}
QLabel#Section {{ font-size: 13pt; font-weight: 600; }}
QLabel#Muted {{ color: {t.muted}; }}
QLabel#Error {{ color: {t.bad}; font-size: 9.5pt; }}
QLabel#Good {{ color: {t.good}; }}
QLabel#Bad {{ color: {t.bad}; }}
QLabel#InfoMark {{ color: {t.accent}; font-size: 9.5pt; }}
QLabel#ExplainTitle {{ font-weight: 600; }}
QLabel#TileValue {{ font-size: 18pt; font-weight: 600; }}
QLabel[tone="good"] {{ color: {t.good}; }}
QLabel[tone="bad"] {{ color: {t.bad}; }}
QFrame#Rule {{ background: {t.rule}; border: none; }}

/* Statements: deductions in brackets, totals double-underlined */
QLabel#Total {{
    padding: 6px 0; font-weight: 600;
    border-top: 1px solid {t.text}; border-bottom: 3px double {t.text};
}}

/* Text boxes and drop-downs: sunk into the page */
QLineEdit, QComboBox {{
    background: {t.well}; border: 1px solid; {sunken}
    border-radius: 12px; padding: 8px 12px; min-height: 18px;
    selection-background-color: {t.accent}; selection-color: {t.on_accent};
}}
QLineEdit:focus, QComboBox:focus {{ border: 2px solid {t.accent}; padding: 7px 11px; }}
QLineEdit[invalid="true"] {{ border: 2px solid {t.bad}; padding: 7px 11px; }}
QComboBox::drop-down {{
    subcontrol-origin: padding; subcontrol-position: center right;
    width: 30px; border: none;
}}
QComboBox::down-arrow {{ image: url("{arrow}"); width: 12px; height: 12px; }}
QComboBox QAbstractItemView {{
    background: {t.page}; color: {t.text}; border: 1px solid {t.edge_dark};
    selection-background-color: {t.accent_soft}; selection-color: {t.text};
    padding: 4px; outline: 0;
}}

/* Buttons: raised out of the page; pressed buttons sink in */
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {t.raised_hi}, stop:1 {t.raised_lo});
    border: 1px solid; {raised}
    border-radius: 12px; padding: 8px 18px; font-weight: 600; color: {t.text};
}}
QPushButton:hover {{ color: {t.accent}; }}
QPushButton:pressed {{ background: {t.well}; {sunken} }}
QPushButton:focus {{ border: 2px solid {t.accent}; padding: 7px 17px; }}
QPushButton:disabled {{ color: {t.faint}; }}
QPushButton#Primary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {t.accent_hi}, stop:1 {t.accent});
    color: {t.on_accent}; border: 1px solid {t.accent};
}}
QPushButton#Primary:hover {{ background: {t.accent_hi}; color: {t.on_accent}; }}
QPushButton#Primary:pressed {{ background: {t.accent}; }}
QPushButton#Primary:focus {{ border: 2px solid {t.text}; padding: 7px 17px; }}

/* Tables, lists and the help text sit on raised cards */
QTableWidget, QListWidget, QTextBrowser {{
    background: {t.page}; border: none; gridline-color: {t.rule};
    selection-background-color: {t.accent_soft}; selection-color: {t.text};
    outline: 0;
}}
QTableWidget::item {{ padding: 4px 8px; border-bottom: 1px solid {t.rule}; }}
QTableWidget::item:selected {{ background: {t.accent_soft}; color: {t.text}; }}
QHeaderView, QHeaderView::section {{ background: {t.page}; }}
QHeaderView::section {{
    border: none; border-bottom: 1px solid {t.edge_dark};
    padding: 8px; font-weight: 600; color: {t.muted};
}}
QTableCornerButton::section {{ background: {t.page}; border: none; }}
QListWidget::item {{ padding: 10px 12px; border-radius: 10px; margin: 2px 0; }}
QListWidget::item:hover {{ background: {t.well}; }}
QListWidget::item:selected {{ background: {t.accent_soft}; color: {t.text}; }}

/* Slim rounded scroll bars */
QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {t.scrollbar}; min-height: 36px; border-radius: 4px; }}
QScrollBar::handle:horizontal {{ background: {t.scrollbar}; min-width: 36px; border-radius: 4px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}

/* Info boxes */
QToolTip {{
    background: {t.page}; color: {t.text}; border: 1px solid {t.accent};
    padding: 8px 10px; font-size: 10pt;
}}
"""
