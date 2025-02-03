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
)
from PyQt6.QtGui import QTextCursor
import initialize
import youtube_api
import downloader
import spotify_api
from syncer import SyncWorker

""" Notes:
- Ctr + Shft + J to beautify json
- Figure out what to do about the button / message when a user is already authenticated. Sketchy cuz the token could expire. 
- Test new authorization
"""


class OutputStream:
    """
    Custom stream to redirect stdout to a QTextEdit widget.
    """

    def __init__(self, text_edit, original_stream):
        self.text_edit = text_edit
        self.original_stream = original_stream

    def write(self, message: str):
        if message.strip():
            # Write to the QTextEdit 'terminal' widget
            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            self.text_edit.append(f"{timestamp} {message.strip()}")
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

            # Also write to the original stream (terminal)
            if not message.endswith("\n"):
                message += "\n"
            self.original_stream.write(message)

    def flush(self):
        self.original_stream.flush()


class DirectoryInputApp(QWidget):
    youtube_creds = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DownAndSync")

        # Create layout
        main_layout = QVBoxLayout()

        # Authentication with Youtube
        youtube_auth_button = QPushButton("Authorize Youtube")
        youtube_auth_button.clicked.connect(self.set_youtube_creds)
        main_layout.addWidget(youtube_auth_button)

        # Authentication with Spotify
        spotify_auth_button = QPushButton("Authorize Spotify")
        spotify_auth_button.clicked.connect(self.set_spotify_creds)
        main_layout.addWidget(spotify_auth_button)

        main_layout.addLayout(self.create_directory_input_widget())

        # Thread vars
        self.download_thread = None
        self.worker = False
        self.sync_worker = None
        self.sync_thread = None
        self.sync_running = False

        main_layout.addLayout(self.create_downloading_process_widget())
        main_layout.addLayout(self.create_syncer_test_widget())

        # Terminal
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFixedHeight(200)
        main_layout.addWidget(self.terminal)

        self.setMinimumSize(QSize(600, 400))
        self.setLayout(main_layout)
        self.load_existing_directory_path()

        # These lines (or one of them) randomly crash the app, but useful for IDE terminal logs
        # sys.stdout = OutputStream(self.terminal, sys.__stdout__)
        # sys.stderr = OutputStream(self.terminal, sys.__stderr__)

    def create_directory_input_widget(self) -> QVBoxLayout:
        """
        Creates the label, QLineEdit, and QPushButton for directory input.
        Returns the layout containing these widgets.
        """
        # Vertical layout for label and input
        layout = QVBoxLayout()

        # Label to show instructions
        label = QLabel("Enter the directory path used by your plex server:")
        layout.addWidget(label)

        # Horizontal layout for input line and button
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setFixedWidth(300)  # Set a fixed width for the input line
        input_layout.addWidget(self.input_line)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.open_directory_dialog)
        browse_button.setMaximumWidth(100)
        input_layout.addWidget(browse_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_directory_path)
        save_button.setMaximumWidth(100)
        input_layout.addWidget(save_button)

        # Add the horizontal layout to the vertical layout
        layout.addLayout(input_layout)

        return layout

    def create_syncer_test_widget(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        start_sync_button = QPushButton("Start Sync")
        start_sync_button.clicked.connect(self.start_sync_test)
        layout.addWidget(start_sync_button)

        cancel_button = QPushButton("Stop Sync")
        cancel_button.clicked.connect(self.stop_sync_test)
        layout.addWidget(cancel_button)

        return layout

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

    def create_downloading_process_widget(self) -> QHBoxLayout:
        """
        Creates the download and cancel button, returns a layout.
        """
        layout = QHBoxLayout()
        download_liked_videos_button = QPushButton("Download all liked videos")
        download_liked_videos_button.clicked.connect(
            self.start_downloading_liked_videos
        )
        layout.addWidget(download_liked_videos_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_download_liked_videos)
        layout.addWidget(cancel_button)

        return layout

    def start_downloading_liked_videos(self) -> None:
        def fetch_liked_videos() -> None:
            if not self.youtube_creds:
                print(
                    "Youtube credentials not set, prompting authorize youtube process:"
                )
                self.set_youtube_creds()
            # Change number upon prod.
            return youtube_api.fetch_liked_videos(self.youtube_creds, 5)

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

    def open_directory_dialog(self) -> None:
        # Open a directory dialog and set the selected path to the input line
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.input_line.setText(directory)

    def save_directory_path(self) -> None:
        """
        Records the directory path selected by the user in directory dialog prompt
        """
        self.selected_directory = self.input_line.text()
        if self.selected_directory:
            config = initialize.load_config()
            config["directory_path"] = self.selected_directory
            initialize.save_config(config)
            print(f"Directory path saved: {self.selected_directory}")
        else:
            print("Error saving directory path")

    def cancel_download_liked_videos(self) -> None:
        if self.worker:
            self.worker.cancel_download = True

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
    window = DirectoryInputApp()
    window.show()
    sys.exit(app.exec())
