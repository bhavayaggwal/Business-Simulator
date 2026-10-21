"""Visual theme: an accountant's ledger.

Pale ruled-paper background, ink-navy text, ledger green for profit and a
muted red for losses. Headings use Georgia (a book face, like a printed
ledger); everything else uses the system UI font.
"""
from decimal import Decimal

from PyQt6.QtWidgets import QProxyStyle, QStyle, QStyleFactory

PAPER = "#F3F5F0"      # page background
SHEET = "#FFFFFF"      # statement / panel background
INK = "#1E2B3A"        # main text and navigation bar
MUTED = "#5B6876"      # secondary text
RULE = "#D5DCCF"       # ledger rule lines
LEDGER_GREEN = "#2F6B4F"
LEDGER_GREEN_SOFT = "#E3EEE6"
LOSS_RED = "#A63D32"
OCHRE = "#B07D2B"      # third chart colour (cash)

HEADING_FONT = "Georgia"
BODY_FONT = "Segoe UI"

TOOLTIP_DELAY_MS = 400  # info boxes appear within 0.5 s (objective 18)


class InfoBoxStyle(QProxyStyle):
    """Fusion style with a shorter tooltip delay."""

    def __init__(self):
        super().__init__(QStyleFactory.create("Fusion"))

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.StyleHint.SH_ToolTip_WakeUpDelay:
            return TOOLTIP_DELAY_MS
        return super().styleHint(hint, option, widget, returnData)


def fmt_money(value) -> str:
    """£1,234.56 or −£40.00"""
    value = Decimal(value)
    sign = "−" if value < 0 else ""
    return f"{sign}£{abs(value):,.2f}"


def fmt_deduction(value) -> str:
    """Accounting style: amounts taken away are shown in brackets."""
    return f"({fmt_money(value)})"


def fmt_units(value) -> str:
    return f"{value:,}"


STYLESHEET = f"""
QWidget {{
    font-family: "{BODY_FONT}", "Helvetica Neue", Arial;
    font-size: 10.5pt;
    color: {INK};
}}
QMainWindow, QStackedWidget, QScrollArea, QScrollArea > QWidget > QWidget {{
    background: {PAPER};
}}

/* Navigation bar */
#NavBar {{ background: {INK}; }}
#NavBar QLabel#AppName {{
    color: {PAPER}; font-family: "{HEADING_FONT}"; font-size: 13pt;
}}
#NavBar QPushButton {{
    color: #C9D3DC; background: transparent; border: none;
    padding: 6px 12px; font-size: 10pt;
}}
#NavBar QPushButton:hover {{ color: {PAPER}; }}
#NavBar QPushButton:checked {{ color: {PAPER}; border-bottom: 2px solid {LEDGER_GREEN_SOFT}; }}
#NavBar QPushButton:disabled {{ color: #6D7B89; }}
#NavBar QLabel#WhoAmI {{ color: #9AA8B5; font-size: 9.5pt; }}

/* Type */
QLabel#Title {{ font-family: "{HEADING_FONT}"; font-size: 20pt; }}
QLabel#Subtitle {{ color: {MUTED}; font-size: 10.5pt; }}
QLabel#Section {{ font-family: "{HEADING_FONT}"; font-size: 13pt; padding-top: 8px; }}
QLabel#Muted {{ color: {MUTED}; }}
QLabel#Error {{ color: {LOSS_RED}; font-size: 9.5pt; }}
QLabel#Good {{ color: {LEDGER_GREEN}; }}
QLabel#Bad {{ color: {LOSS_RED}; }}
QLabel#InfoMark {{ color: {LEDGER_GREEN}; font-size: 9.5pt; }}

/* Statement sheet (results screen) */
QFrame#Sheet {{
    background: {SHEET}; border: 1px solid {RULE};
}}
QLabel#Line {{ padding: 5px 0; border-bottom: 1px solid {RULE}; }}
QLabel#Amount {{ padding: 5px 0; border-bottom: 1px solid {RULE}; }}
QLabel#TotalLabel {{ padding: 6px 0; font-weight: 600; }}
QLabel#Total {{
    padding: 6px 0; font-weight: 600;
    border-top: 1px solid {INK}; border-bottom: 3px double {INK};
}}

/* Panels and tiles */
QFrame#Panel {{ background: {SHEET}; border: 1px solid {RULE}; }}
QLabel#TileValue {{ font-family: "{HEADING_FONT}"; font-size: 17pt; }}
QFrame#Explain {{ background: {LEDGER_GREEN_SOFT}; border-left: 3px solid {LEDGER_GREEN}; }}

/* Inputs */
QLineEdit, QComboBox {{
    background: {SHEET}; border: 1px solid #B9C3B4; padding: 6px 8px; min-height: 18px;
}}
QLineEdit:focus, QComboBox:focus {{ border: 1px solid {LEDGER_GREEN}; }}
QLineEdit[invalid="true"] {{ border: 1px solid {LOSS_RED}; }}

/* Buttons */
QPushButton {{
    background: {SHEET}; border: 1px solid #B9C3B4; padding: 7px 16px;
}}
QPushButton:hover {{ border-color: {INK}; }}
QPushButton:focus {{ border: 1px solid {LEDGER_GREEN}; }}
QPushButton#Primary {{
    background: {LEDGER_GREEN}; color: {SHEET}; border: 1px solid {LEDGER_GREEN};
    font-weight: 600;
}}
QPushButton#Primary:hover {{ background: #255840; }}
QPushButton:disabled {{ color: #9AA5A0; border-color: {RULE}; }}

/* Tables and lists */
QTableWidget, QListWidget, QTextBrowser {{
    background: {SHEET}; border: 1px solid {RULE}; gridline-color: {RULE};
    selection-background-color: {LEDGER_GREEN_SOFT}; selection-color: {INK};
}}
QHeaderView::section {{
    background: {PAPER}; border: none; border-bottom: 1px solid {INK};
    padding: 6px; font-weight: 600;
}}
QListWidget::item {{ padding: 8px; border-bottom: 1px solid {RULE}; }}

/* Info boxes */
QToolTip {{
    background: {SHEET}; color: {INK}; border: 1px solid {LEDGER_GREEN};
    padding: 8px; font-size: 10pt;
}}
"""
