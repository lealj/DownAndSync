import os
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QTextEdit,
    QWidget,
    QFrame,
)
from PyQt6.QtGui import QIcon, QPixmap
from app.core.youtube_service import setup_liked_videos
from app.core.config import get_directory_path
from app.gui.window_bar_widget import WindowTitleBar


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

    browse_button = create_singleton_button(open_directory_dialog, "Browse")
    browse_button.setMaximumWidth(100)
    input_layout.addWidget(browse_button)

    save_button = create_singleton_button(save_directory_path, "Save")
    save_button.setMaximumWidth(100)
    input_layout.addWidget(save_button)

    # Add the horizontal layout to the vertical layout
    layout.addLayout(input_layout)

    return layout


def create_syncer_test_layout(start_sync_test, stop_sync_test) -> QVBoxLayout:
    layout = QVBoxLayout()
    start_sync_button = create_singleton_button(start_sync_test, "Start Sync")
    layout.addWidget(start_sync_button)

    cancel_button = create_singleton_button(stop_sync_test, "Stop Sync")
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
    download_liked_videos_button.setObjectName("default_btn")
    layout.addWidget(download_liked_videos_button)

    cancel_button = create_singleton_button(cancel_download_liked_videos, "Cancel")
    layout.addWidget(cancel_button)

    return layout


def create_terminal_widget() -> QTextEdit:
    terminal = QTextEdit()
    terminal.setReadOnly(True)
    terminal.setFixedHeight(200)
    return terminal


def create_singleton_button(callback, text="", style=None, icon=None) -> QPushButton:
    button = QPushButton(text)
    button.clicked.connect(callback)
    if style:
        button.setObjectName(style)
    else:
        button.setObjectName("default_btn")

    if icon:
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", icon
        )
        icon = QIcon(icon_path)
        button.setIcon(icon)
    return button


def create_window_bar_widget(main_window) -> QWidget:
    return WindowTitleBar(main_window, create_singleton_button)
