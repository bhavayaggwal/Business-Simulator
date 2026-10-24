"""How figures are written, and the tooltip timing.

Colours and the style sheet live in ui/theme.py (light and dark themes).
Figures follow accounting conventions in both themes: amounts taken away are
shown in brackets, and totals are double-underlined.
"""
from decimal import Decimal

from PyQt6.QtWidgets import QProxyStyle, QStyle, QStyleFactory

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
