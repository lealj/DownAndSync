import sys
import os
import datetime
import json
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel, QHBoxLayout, QTextEdit
)
from PyQt6.QtGui import QTextCursor
import initialize
import threading
import youtube_api
from downloader import download_liked_videos
import spotify_api

''' Notes:
- Ctr + Shft + J to beautify json
- Figure out what to do about the button / message when a user is already authenticated. Sketchy cuz the token could expire. 
- Test new authorization
'''
class OutputStream:
    """
    Custom stream to redirect stdout to a QTextEdit widget.
    """
    def __init__(self, text_edit):
        self.text_edit = text_edit


    def write(self, message):
        if message.strip():
            # Write to the QTextEdit 'terminal' widget
            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            self.text_edit.append(f"{timestamp} {message.strip()}")
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)
            
            # Also write to the original stream (terminal)
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

        # Authentication with youtube
        youtube_auth_button = QPushButton("Authorize Youtube")
        youtube_auth_button.clicked.connect(self.set_youtube_creds)
        main_layout.addWidget(youtube_auth_button)

        spotify_auth_button = QPushButton("Authorize Spotify")
        spotify_auth_button.clicked.connect(self.set_spotify_creds)
        main_layout.addWidget(spotify_auth_button)

        main_layout.addLayout(self.create_directory_input_widget())

        # Thread / Cancel Flag
        self.download_thread = None
        self.cancel_downloads = False

        main_layout.addLayout(self.create_downloading_process_widget())

        # Terminal
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFixedHeight(200)
        main_layout.addWidget(self.terminal)

        self.setMinimumSize(QSize(600, 400))
        self.setLayout(main_layout)
        self.load_existing_directory_path()

        sys.stdout = OutputStream(self.terminal, sys.__stdout__)
        sys.stderr = OutputStream(self.terminal, sys.__stderr__)

    
    def create_directory_input_widget(self):
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
    

    def create_downloading_process_widget(self):
        """
        Creates the download and cancel button, returns a layout.
        """
        layout = QHBoxLayout()
        download_liked_videos_button = QPushButton("Download all liked videos")
        download_liked_videos_button.clicked.connect(self.start_downloading_liked_videos)
        layout.addWidget(download_liked_videos_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_download_liked_videos)
        layout.addWidget(cancel_button)

        return layout
    

    def load_existing_directory_path(self):
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


    def open_directory_dialog(self):
        # Open a directory dialog and set the selected path to the input line
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.input_line.setText(directory)


    def save_directory_path(self):
        self.selected_directory = self.input_line.text()
        if self.selected_directory:
            config = initialize.load_config()
            config['directory_path'] = self.selected_directory
            initialize.save_config(config)
            print(f"Directory path saved: {self.selected_directory}")
        else:
            print("Error saving directory path")


    def start_downloading_liked_videos(self):
        if self.download_thread and self.download_thread.is_alive():
            print("Download process is already running.")
            return
        
        self.cancel_download = False  # Reset the cancellation flag
        self.download_thread = threading.Thread(target=self.fetch_liked_videos)
        self.download_thread.start()


    def set_creds(self):
        self.creds = youtube_api.youtube_authentication()


    def fetch_liked_videos(self):
        if not self.youtube_creds:
            print("Youtube credentials not set, prompting authorize youtube process:")
            self.set_youtube_creds()
        youtube_api.fetch_liked_videos(self.youtube_creds)
        download_liked_videos(self)
    
    
    def cancel_download_liked_videos(self):
        self.cancel_download = True
        print("Cancel downloading requested")

        
    def set_youtube_creds(self):
        self.youtube_creds = youtube_api.youtube_authentication()

        
    def set_spotify_creds(self):
        self.spotify_creds = spotify_api.spotify_authentication()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    initialize.initialize_config()
    window = DirectoryInputApp()
    window.show()
    sys.exit(app.exec())