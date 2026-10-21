"""Help: the glossary (same text as the info boxes) and how to use each screen."""
from PyQt6.QtWidgets import QTextBrowser

from ui.style import HEADING_FONT, LEDGER_GREEN, MUTED, RULE
from ui.widgets import Screen

HOW_TO = [
    ("Your businesses", "Lists every business in your profile. Search by name or "
     "industry, open a business to carry on, or start a new one."),
    ("Start a new business", "Pick an industry, then set your starting cash, price, "
     "stock and marketing. The industry figures are filled in for you; change them if "
     "you like."),
    ("Business hub", "Shows your cash, stock and last month's results. Every other "
     "business screen starts here."),
    ("Decisions", "Set this month's price, marketing and how much stock to buy. The "
     "panel on the right shows how much cash the plan leaves you."),
    ("Month results", "A profit and loss statement beside a cash statement, so you can "
     "see why profit and cash change by different amounts."),
    ("History", "Every month in a table. Sort by profit, revenue, costs or cash, or "
     "type a month number to jump to it."),
    ("Graphs", "Trends over time, where your money went, and revenue against costs. "
     "You can compare profit with another of your businesses."),
]


class HelpScreen(Screen):
    def __init__(self, app):
        super().__init__(app, "Help",
                         "Key business terms, and how to use each screen. Hover over "
                         "any ⓘ in the app to see a term's definition where you are.")
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setMinimumHeight(520)
        self.body.addWidget(self.browser)

    def refresh(self):
        terms = "".join(
            f"<p style='margin:0 0 12px 0'><b>{t.term}</b><br>{t.definition}"
            + (f"<br><span style='color:{MUTED}'>Example: {t.example}</span>"
               if t.example else "")
            + "</p>"
            for t in self.app.glossary.values())
        screens = "".join(f"<p style='margin:0 0 10px 0'><b>{name}</b><br>{text}</p>"
                          for name, text in HOW_TO)
        heading = (f"style=\"font-family:'{HEADING_FONT}'; font-size:14pt; "
                   f"color:{LEDGER_GREEN}; border-bottom:1px solid {RULE}\"")
        self.browser.setHtml(
            f"<h2 {heading}>Business terms</h2>{terms}"
            f"<h2 {heading}>Using the simulator</h2>{screens}")
