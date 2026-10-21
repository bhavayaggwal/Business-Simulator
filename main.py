"""Business Startup Simulator: start the app.

Prototype build: data is held in memory (data/memory_repository.py) and a demo
profile with six months of history is created on start-up, so every screen
has realistic data. The SQL Server repository replaces it in a later iteration.
"""
import sys

from PyQt6.QtWidgets import QApplication

from data.memory_repository import MemoryRepository
from logic.services import SimulatorService, seed_demo
from ui.main_window import MainWindow
from ui.style import STYLESHEET, InfoBoxStyle


def main():
    app = QApplication(sys.argv)
    app.setStyle(InfoBoxStyle())
    app.setStyleSheet(STYLESHEET)

    service = SimulatorService(MemoryRepository())
    seed_demo(service)

    window = MainWindow(service)
    window.resize(1180, 820)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
