from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
import os


class SystemTray(QSystemTrayIcon):
    def __init__(self, parent):
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "icon.ico"
        )
        super().__init__(QIcon(icon_path), parent)
        self.setToolTip("DownAndSync")

        menu = QMenu(parent)
        restore_action = QAction("Restore", parent)
        restore_action.triggered.connect(parent.show)
        menu.addAction(restore_action)

        quit_action = QAction("Quit", parent)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.activated.connect(self.on_tray_icon_clicked)
        self.show()

    def on_tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.parent().show()
