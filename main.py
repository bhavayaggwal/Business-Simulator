"""Business Startup Simulator: start the app.

    python main.py          use the SQL Server database (run setup_db.py once first)
    python main.py --demo   use demo data held in memory; nothing is saved

main.py is the one place that decides which repository the program uses. The
screens and the logic never know whether data lives in memory or SQL Server.
"""
import argparse
import sys
import traceback

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication, QMessageBox

from data.connection import load_settings
from data.memory_repository import MemoryRepository
from data.sql_repository import SqlRepository
from logic.errors import StorageError
from logic.services import SimulatorService, seed_demo
from ui.main_window import MainWindow
from ui.soft import apply_theme, set_dark_title_bar
from ui.style import InfoBoxStyle

APP_NAME = "Business Simulator"


def demo_service():
    service = SimulatorService(MemoryRepository())
    seed_demo(service)
    return service


def ask_what_next(message):
    """Ask what to do when the database can't be used: 'retry', 'demo' or 'quit'."""
    box = QMessageBox(QMessageBox.Icon.Warning, APP_NAME,
                      f"{message}\n\nWhat would you like to do?")
    retry = box.addButton("Try again", QMessageBox.ButtonRole.AcceptRole)
    demo = box.addButton("Use demo mode", QMessageBox.ButtonRole.ActionRole)
    box.addButton("Quit", QMessageBox.ButtonRole.RejectRole)
    box.exec()
    if box.clickedButton() is retry:
        return "retry"
    if box.clickedButton() is demo:
        return "demo"
    return "quit"


def database_service():
    """Connect to SQL Server. Returns (service, is_demo), or (None, False) to quit."""
    while True:
        try:
            repository = SqlRepository(load_settings())
            repository.check_connection()
            return SimulatorService(repository), False
        except (FileNotFoundError, StorageError) as error:
            choice = ask_what_next(str(error))
            if choice == "demo":
                return demo_service(), True
            if choice == "quit":
                return None, False


def show_unexpected_error(error_type, error, error_traceback):
    """Runs for any error a screen didn't catch, so the app shows a message
    instead of closing. (PyQt6 ends the program if this isn't set.)"""
    traceback.print_exception(error_type, error, error_traceback)
    if issubclass(error_type, StorageError):
        message = str(error)
    else:
        message = ("Something went wrong and that action didn't finish. "
                   "The details are in the console window.")
    QMessageBox.warning(None, APP_NAME, message)


def main():
    parser = argparse.ArgumentParser(description="Business Startup Simulator")
    parser.add_argument("--demo", action="store_true",
                        help="use demo data in memory instead of SQL Server")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setStyle(InfoBoxStyle())
    # The light/dark choice is remembered per Windows user (QSettings), not in
    # the database: it is a preference for this laptop, not business data.
    preferences = QSettings("BusinessSimulator", "BusinessSimulator")
    theme_name = preferences.value("theme", "light")
    apply_theme(app, theme_name)
    sys.excepthook = show_unexpected_error

    if args.demo:
        service, is_demo = demo_service(), True
    else:
        service, is_demo = database_service()
    if service is None:
        return 0

    window = MainWindow(service, preferences)
    if is_demo:
        window.setWindowTitle(f"{window.windowTitle()} (demo: nothing is saved)")
    window.resize(1200, 840)
    window.show()
    set_dark_title_bar(window, theme_name == "dark")
    exit_code = app.exec()
    service.repo.close()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
