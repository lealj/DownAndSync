import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from app.gui.main_window import DownAndSync
import app.core.config as config
import os

"""
GUI Components (ui/): Contains UI-related code, such as QMainWindow-derived classes.
Business Logic (core/ or services/): Handles application logic like API interactions and downloads.
Threads & Workers (workers/): Contains classes for background processing, such as downloading YouTube videos.
Configuration & Utilities (config/ & utils/): Handles initialization, settings, and helper functions.
Main Entry Point (main.py): Initializes the application and loads the main window.
"""


def load_dark_mode(app, path):
    with open(path, "r") as f:
        app.setStyleSheet(f.read())


def main():
    my_app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
    icon = QIcon(icon_path)
    my_app.setWindowIcon(icon)
    config.initialize_config()
    dark_mode_path = os.path.join(os.path.dirname(__file__), "styles", "dark_theme.qss")
    load_dark_mode(my_app, dark_mode_path)
    window = DownAndSync()
    window.show()

    sys.exit(my_app.exec())


if __name__ == "__main__":
    main()
