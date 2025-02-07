from PyQt6.QtCore import QObject, pyqtSignal


class SyncWorker(QObject):
    new_like_signal = pyqtSignal(str)

    def check_liked_videos(self):
        while True:
            # Check for new liked videos
            self.new_like_signal.emit("New liked video found!")
