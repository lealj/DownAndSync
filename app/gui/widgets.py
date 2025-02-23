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


def create_fullscreen_button(main_window) -> QWidget:
    def toggle_fullscreen():
        if main_window.is_fullscreen:
            main_window.showNormal()
            main_window.is_fullscreen = False
            fullscreen_button.setText("☐")
        else:
            main_window.showMaximized()
            main_window.is_fullscreen = True
            fullscreen_button.setText("❐")

    fullscreen_button = QPushButton("☐")
    fullscreen_button.clicked.connect(toggle_fullscreen)
    fullscreen_button.setFixedSize(35, 30)
    fullscreen_button.setObjectName("window_btn")
    return fullscreen_button


def create_window_bar_widget(main_window) -> QWidget:
    title_bar = QWidget()
    title_bar.setFixedHeight(40)

    # This should cause the app icon to display in top left when added to layout.
    title_icon_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "assets", "icon.ico"
    )
    title_icon_label = QLabel()
    title_icon_label.setPixmap(QPixmap(title_icon_path))

    title_label = QLabel("    DownAndSync")

    # Creates the x button widget that should close the app upon click.
    close_button = create_singleton_button(
        main_window.close, "", "close_btn", "xmark-solid.svg"
    )
    close_button.setFixedSize(35, 30)

    # Creates the _ button widget that should minimize app to taskbar on click.
    minimize_button = create_singleton_button(
        main_window.showMinimized, "", "window_btn", "window-minimize-solid"
    )
    minimize_button.setFixedSize(35, 30)

    # Creates the window button widget that should fullscreen/smallscreen on click.
    if not hasattr(main_window, "is_fullscreen"):
        main_window.is_fullscreen = False
    fullscreen_button = create_fullscreen_button(main_window)

    # Adds widgets such that all appear in same horizontal area.
    title_layout = QHBoxLayout()
    title_layout.addWidget(title_icon_label)
    title_layout.addWidget(title_label)
    title_layout.addStretch(1)
    title_layout.addWidget(minimize_button)
    title_layout.addWidget(fullscreen_button)
    title_layout.addWidget(close_button)
    title_layout.setContentsMargins(10, 0, 10, 0)

    # Seperator line.
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFrameShadow(QFrame.Shadow.Raised)
    separator.setStyleSheet("background-color: #444;")

    # Stack the title bar and separator.
    container_layout = QVBoxLayout()
    container_layout.addLayout(title_layout)
    container_layout.addWidget(separator)
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_layout.setSpacing(0)

    title_bar.setLayout(container_layout)

    return title_bar
