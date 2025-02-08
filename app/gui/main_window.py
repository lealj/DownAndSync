import datetime
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtCore import QSize, QThread
from PyQt6.QtGui import QTextCursor, QIcon
from PyQt6.QtWidgets import QLineEdit

# from app.gui.tray_icon import SystemTray
from app.gui.widgets import (
    create_singleton_button,
    create_directory_input_layout,
    create_terminal_widget,
    create_downloading_process_layout,
    input_line_init,
)
from app.core.api_auth import YoutubeAuth, SpotifyAuth
from app.threads.download_worker import DownloadWorker
from app.threads.sync_worker import SyncWorker
from app.core.config import load_config, save_config
import os


class DownAndSync(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DownAndSync")
        self.setMinimumSize(QSize(600, 400))

        self.input_line = None
        self.spotify_creds = None

        self.download_thread = None
        self.download_worker = None
        self.download_thread_setup()
        self.sync_thread = None
        self.sync_worker = None

        # idk
        self.sync_running = False
        self.terminal = None

        # self.tray_icon = SystemTray(self)
        self.setup_ui()

    def setup_ui(self):
        """Set up main window UI components"""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        main_layout.addWidget(
            create_singleton_button("Authorize Youtube", self.set_youtube_creds)
        )
        main_layout.addWidget(
            create_singleton_button("Authorize Spotify", self.set_spotify_creds)
        )

        self.input_line = input_line_init()
        dir_input_widget = create_directory_input_layout(
            self.open_directory_dialog, self.save_directory_path, self.input_line
        )
        main_layout.addLayout(dir_input_widget)

        download_process_layout = create_downloading_process_layout(
            self.download_thread_setup,
            self.download_thread_start,
            self.cancel_download_liked_videos,
        )
        main_layout.addLayout(download_process_layout)

        self.terminal = create_terminal_widget()
        main_layout.addWidget(self.terminal)

    def set_youtube_creds(self):
        self.youtube_creds = YoutubeAuth.authentication()

    def set_spotify_creds(self):
        self.spotify_creds = SpotifyAuth.authentication()

    def open_directory_dialog(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.input_line.setText(directory)

    def save_directory_path(self) -> None:
        self.selected_directory = self.input_line.text()
        if self.selected_directory:
            config = load_config()
            config["directory_path"] = self.selected_directory
            save_config(config)
            print(f"Directory path saved: {self.selected_directory}")
        else:
            print("Error saving directory path")

    def download_thread_setup(self):
        self.download_worker = DownloadWorker(self)
        self.download_thread = QThread()
        self.download_worker.moveToThread(self.download_thread)
        self.download_worker.progress.connect(self.append_to_terminal)
        self.download_worker.finished.connect(self.download_thread.quit)
        self.download_worker.finished.connect(self.download_worker.deleteLater)
        self.download_thread.started.connect(self.download_worker.run)

    def download_thread_start(self):
        self.download_thread.start()

    def cancel_download_liked_videos(self) -> None:
        if self.download_worker:
            self.download_worker.cancel_download = True

    # This probably doesn't go here.
    def append_to_terminal(self, message: str):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        self.terminal.append(f"{timestamp} {message}")
        self.terminal.moveCursor(QTextCursor.MoveOperation.End)
