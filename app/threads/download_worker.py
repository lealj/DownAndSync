from PyQt6.QtCore import QObject, pyqtSignal


class DownloadWorker(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, youtube_service parent=None):
        super().__init__()
        self.youtube_service = youtube_service
        self.cancel_download = False

    def run(self):
        try:
            videos = self.youtube_service.fetch_liked_videos()
        except Exception as e:
            
        self.finished.emit()
