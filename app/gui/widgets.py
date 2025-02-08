from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QTextEdit,
)
from app.core.youtube_service import setup_liked_videos
from app.core.config import save_directory_path, get_directory_path


def input_line_init() -> QLineEdit:
    input_line = QLineEdit()
    input_line.setFixedWidth(300)
    path = get_directory_path()
    if path:
        input_line.setText(path)
    return input_line


def create_directory_input_layout(
    open_directory_dialog, save_directory_path, input_line
) -> QVBoxLayout:
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

    input_layout.addWidget(input_line)

    browse_button = QPushButton("Browse")
    browse_button.clicked.connect(open_directory_dialog)
    browse_button.setMaximumWidth(100)
    input_layout.addWidget(browse_button)

    save_button = QPushButton("Save")
    save_button.clicked.connect(save_directory_path)
    save_button.setMaximumWidth(100)
    input_layout.addWidget(save_button)

    # Add the horizontal layout to the vertical layout
    layout.addLayout(input_layout)

    return layout


def create_syncer_test_layout(start_sync_test, stop_sync_test) -> QVBoxLayout:
    layout = QVBoxLayout()
    start_sync_button = QPushButton("Start Sync")
    start_sync_button.clicked.connect(start_sync_test)
    layout.addWidget(start_sync_button)

    cancel_button = QPushButton("Stop Sync")
    cancel_button.clicked.connect(stop_sync_test)
    layout.addWidget(cancel_button)

    return layout


def create_downloading_process_layout(
    download_thread_setup, download_thread_start, cancel_download_liked_videos
) -> QHBoxLayout:
    """
    Creates the download and cancel button, returns a layout.
    """
    layout = QHBoxLayout()
    download_liked_videos_button = QPushButton("Download all liked videos")
    download_liked_videos_button.clicked.connect(setup_liked_videos)
    download_liked_videos_button.clicked.connect(download_thread_setup)
    download_liked_videos_button.clicked.connect(download_thread_start)
    layout.addWidget(download_liked_videos_button)

    cancel_button = QPushButton("Cancel")
    cancel_button.clicked.connect(cancel_download_liked_videos)
    layout.addWidget(cancel_button)

    return layout


def create_terminal_widget() -> QTextEdit:
    terminal = QTextEdit()
    terminal.setReadOnly(True)
    terminal.setFixedHeight(200)
    return terminal


def create_singleton_button(text: str, callback) -> QPushButton:
    button = QPushButton(text)
    button.clicked.connect(callback)
    return button
