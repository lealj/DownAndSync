from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtCore import QSize

# from app.gui.tray_icon import SystemTray
from app.gui.widgets import (
    create_singleton_button,
    create_directory_input_widget,
    create_terminal_widget,
)
from app.core.auth import YoutubeAuth, SpotifyAuth
from app.threads.download_worker import DownloadWorker
from app.threads.sync_worker import SyncWorker
from app.core.config import open_directory_dialog, save_config, load_config


class DownAndSync(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DownAndSync")
        self.setMinimumSize(QSize(600, 400))

        self.input_line = None
        self.youtube_creds = None
        self.spotify_creds = None
        self.download_thread = None
        self.sync_thread = None
        self.sync_running = False

        # self.tray_icon = SystemTray(self)
        self.setup_ui()
        self.load_existing_directory_path()

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

        dir_input_widget, self.input_line = create_directory_input_widget(
            self.open_directory_dialog, self.save_directory_path
        )
        main_layout.addLayout(dir_input_widget)

        main_layout.addWidget(create_terminal_widget())

    def set_youtube_creds(self):
        self.youtube_creds = YoutubeAuth.authentication()

    def set_spotify_creds(self):
        self.spotify_creds = SpotifyAuth.authentication()

    # def closeEvent(self, event):
    #     """Minimizes the application to the system tray instead of closing."""
    #     event.ignore()
    #     self.hide()
    #     self.tray_icon.showMessage("DownAndSync", "Minimized to system tray")

    def open_directory_dialog(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.input_line.setText(directory)

    def save_directory_path(self) -> None:
        """
        Records the directory path selected by the user in directory dialog prompt
        """
        self.selected_directory = self.input_line.text()
        if self.selected_directory:
            current_config = load_config()
            current_config["directory_path"] = self.selected_directory
            save_config(current_config)
            print(f"Directory path saved: {self.selected_directory}")
        else:
            print("Error saving directory path")

    def start_downloading_liked_videos(self) -> None:
        """
        Initiates the process of downloading liked YouTube videos.
        Creates worker and thread for download process.
        """

        liked_videos = fetch_liked_videos()
        youtube_api.insert_liked_videos(liked_videos)
        if liked_videos is None:
            print("Failed to retrieve liked videos.")
            return

        if self.download_thread and self.download_thread.isRunning():
            print("Download process is already running.")
            return

        self.worker = downloader.DownloadWorker(self)
        self.download_thread = QThread()

        self.worker.moveToThread(self.download_thread)

        # Connect signals
        self.worker.progress.connect(self.append_to_terminal)
        self.worker.finished.connect(self.download_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.download_thread.finished.connect(self.download_thread.deleteLater)

        # Call run function when thread started
        self.download_thread.started.connect(self.worker.run)

        self.download_thread.start()
