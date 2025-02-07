# from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QAction
# from PyQt6.QtGui import QIcon


# class SystemTray(QSystemTrayIcon):
#     def __init__(self, parent):
#         super().__init__(QIcon("downandsync/assets/icons/app_icon.png"), parent)
#         self.setToolTip("DownAndSync")

#         menu = QMenu(parent)
#         restore_action = QAction("Restore", parent)
#         restore_action.triggered.connect(parent.show)
#         menu.addAction(restore_action)

#         quit_action = QAction("Quit", parent)
#         quit_action.triggered.connect(parent.quit)
#         menu.addAction(quit_action)

#         self.setContextMenu(menu)
#         self.activated.connect(self.on_tray_icon_clicked)
#         self.show()

#     def on_tray_icon_clicked(self, reason):
#         if reason == QSystemTrayIcon.ActivationReason.Trigger:
#             self.parent().show()
