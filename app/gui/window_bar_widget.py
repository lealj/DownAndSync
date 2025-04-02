from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QPushButton,
)
from PyQt6.QtGui import QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, QPoint
import os


class WindowTitleBar(QWidget):
    def __init__(self, main_window, create_singleton_button):
        super().__init__()
        self.main_window = main_window
        self.setFixedHeight(40)
        self.setMouseTracking(True)
        self.dragging = False

        # This should cause the app icon to display in top left when added to layout.
        title_icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "icon.ico"
        )
        title_icon_label = QLabel()
        title_icon_label.setPixmap(QPixmap(title_icon_path))

        title_label = QLabel("    DownAndSync")

        # Creates the x button widget that should close the app upon click.
        close_button = create_singleton_button(
            self.main_window.close, "", "close_btn", "xmark-solid.svg"
        )
        close_button.setFixedSize(35, 30)

        # Creates the _ button widget that should minimize app to taskbar on click.
        minimize_button = create_singleton_button(
            self.main_window.showMinimized, "", "window_btn", "window-minimize-solid"
        )
        minimize_button.setFixedSize(35, 30)

        # Creates the window button widget that should fullscreen/smallscreen on click.
        if not hasattr(self.main_window, "is_fullscreen"):
            self.main_window.is_fullscreen = False
        fullscreen_button = self.create_fullscreen_button()

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

        self.setLayout(container_layout)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.start_pos = event.globalPosition().toPoint() - self.main_window.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.main_window.move(event.globalPosition().toPoint() - self.start_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False
        event.accept()

    def create_fullscreen_button(self) -> QWidget:
        def toggle_fullscreen():
            if self.main_window.is_fullscreen:
                self.main_window.showNormal()
                self.main_window.is_fullscreen = False
                fullscreen_button.setText("☐")
            else:
                self.main_window.showMaximized()
                self.main_window.is_fullscreen = True
                fullscreen_button.setText("❐")

        fullscreen_button = QPushButton("☐")
        fullscreen_button.clicked.connect(toggle_fullscreen)
        fullscreen_button.setFixedSize(35, 30)
        fullscreen_button.setObjectName("window_btn")
        return fullscreen_button
