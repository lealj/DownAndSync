import sys
import os
import datetime
import json
from PyQt6.QtCore import QSize, Qt, QThread
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QLabel,
    QHBoxLayout,
    QTextEdit,
    QMainWindow,
    QMessageBox,
    QSystemTrayIcon,
)
from PyQt6.QtGui import QTextCursor
import initialize
import youtube_api
import spotify_api
from syncer import SyncWorker
from app.gui import main_widgets

""" Notes:
- Ctr + Shft + J to beautify json
- Figure out what to do about the button / message when a user is already authenticated. Sketchy cuz the token could expire. 
- Test new authorization
"""


class DownAndSync(QMainWindow):
    youtube_creds = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DownAndSync")
        self.input_line = None

        # Create layout
        central_widget = QWidget(self)  # Central widget
        self.setCentralWidget(central_widget)  # Set it as the main widget
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Authentication with Youtube
        main_layout.addWidget(
            main_widgets.create_singleton_button(
                "Authorize Youtube", self.set_youtube_creds
            )
        )

        # Authentication with Spotify
        main_layout.addWidget(
            main_widgets.create_singleton_button(
                "Authorize Spotify", self.set_spotify_creds
            )
        )

        # Add directory input widget
        dir_input_widget, self.input_line = main_widgets.create_directory_input_widget(
            self.open_directory_dialog, self.save_directory_path
        )
        main_layout.addLayout(dir_input_widget)

        # Thread vars
        self.download_thread = None
        self.worker = False
        self.sync_worker = None
        self.sync_thread = None
        self.sync_running = False

        # Add bulk download widgets
        main_layout.addLayout(
            main_widgets.create_downloading_process_widget(
                self.start_downloading_liked_videos, self.cancel_download_liked_videos
            )
        )

        # Add test sync widget
        main_layout.addLayout(
            main_widgets.create_syncer_test_widget(
                self.start_sync_test, self.stop_sync_test
            )
        )

        # Add terminal widget
        self.terminal = main_widgets.create_terminal_widget()
        main_layout.addWidget(self.terminal)

        self.setMinimumSize(QSize(600, 400))
        self.load_existing_directory_path()

        # These lines (or one of them) randomly crash the app, but useful for IDE terminal logs
        # sys.stdout = OutputStream(self.terminal, sys.__stdout__)
        # sys.stderr = OutputStream(self.terminal, sys.__stderr__)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "DownAndSync",
            "Minimized to system tray",
            QSystemTrayIcon.MessageIcon.Information,
        )

    def showWindow(self):
        self.showNormal()
        self.activateWindow()

    def quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()

    def on_tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window()

    def on_window_close(self):
        """Custom function triggered on window close."""
        print("Window is closing. Performing cleanup...")
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.quit()
        if self.sync_thread and self.sync_thread.isRunning():
            self.sync_thread.quit()
        self.showMinimized()

    def start_sync_test(self):
        self.sync_thread = QThread()
        self.sync_worker = SyncWorker()
        self.sync_worker.moveToThread(self.sync_thread)

        self.sync_worker.new_like_signal.connect(self.append_to_terminal)
        self.sync_thread.started.connect(self.sync_worker.check_liked_videos)

        self.sync_thread.start()
        self.sync_running = True

    def stop_sync_test(self):
        if self.sync_worker:
            self.sync_worker.stop()
            self.sync_thread.quit()
            self.sync_thread.wait()
        self.sync_running = False

    # In main_window
    # def start_downloading_liked_videos(self) -> None:
    #     """
    #     Initiates the process of downloading liked YouTube videos.
    #     Creates worker and thread for download process.
    #     """

    #     def fetch_liked_videos() -> None:
    #         if not self.youtube_creds:
    #             print(
    #                 "Youtube credentials not set, prompting authorize youtube process:"
    #             )
    #             self.set_youtube_creds()
    #         # Change number upon prod.
    #         return youtube_api.fetch_liked_videos(self.youtube_creds, 5)

    #     liked_videos = fetch_liked_videos()
    #     youtube_api.insert_liked_videos(liked_videos)
    #     if liked_videos is None:
    #         print("Failed to retrieve liked videos.")
    #         return

    #     if self.download_thread and self.download_thread.isRunning():
    #         print("Download process is already running.")
    #         return

    #     self.worker = downloader.DownloadWorker(self)
    #     self.download_thread = QThread()

    #     self.worker.moveToThread(self.download_thread)

    #     # Connect signals
    #     self.worker.progress.connect(self.append_to_terminal)
    #     self.worker.finished.connect(self.download_thread.quit)
    #     self.worker.finished.connect(self.worker.deleteLater)
    #     self.download_thread.finished.connect(self.download_thread.deleteLater)

    #     # Call run function when thread started
    #     self.download_thread.started.connect(self.worker.run)

    #     self.download_thread.start()

    def load_existing_directory_path(self) -> None:
        """
        Loads the existing directory path from the config file and displays it in the input field.
        """
        try:
            directory_path = initialize.get_directory_path()
            if directory_path:
                self.input_line.setText(directory_path)  # Set the path in the QLineEdit
                print(f"Loaded existing directory path: {directory_path}")
            else:
                print("No existing directory path found in config.")
        except Exception as e:
            print(f"Error loading existing directory path: {e}")

    # In main_window.py
    # def open_directory_dialog(self) -> None:
    #     """
    #     Open a directory dialog and set the selected path to the input line
    #     """
    #     directory = QFileDialog.getExistingDirectory(self, "Select Directory")
    #     if directory:
    #         self.input_line.setText(directory)

    # def save_directory_path(self) -> None:
    #     """
    #     Records the directory path selected by the user in directory dialog prompt
    #     """
    #     self.selected_directory = self.input_line.text()
    #     if self.selected_directory:
    #         config = initialize.load_config()
    #         config["directory_path"] = self.selected_directory
    #         initialize.save_config(config)
    #         print(f"Directory path saved: {self.selected_directory}")
    #     else:
    #         print("Error saving directory path")

    # def cancel_download_liked_videos(self) -> None:
    #     if self.worker:
    #         self.worker.cancel_download = True

    def set_youtube_creds(self) -> None:
        self.youtube_creds = youtube_api.youtube_authentication()

    def set_spotify_creds(self) -> None:
        self.spotify_creds = spotify_api.spotify_authentication()

    def append_to_terminal(self, message: str):
        """
        Append messages to QTextEdit terminal
        """
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        self.terminal.append(f"{timestamp} {message}")
        self.terminal.moveCursor(QTextCursor.MoveOperation.End)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    initialize.initialize_config()
    window = DownAndSync()
    window.show()
    sys.exit(app.exec())
