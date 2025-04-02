from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from app.core.api_auth import YoutubeAuth
from app.core.database import DatabaseManager
from app.core.youtube_service import fetch_liked_videos
from app.threads.download_worker import DownloadWorker
import threading


class SyncWorker(QObject):
    new_like_signal = pyqtSignal(str)

    def __init__(self, check_interval=60):
        super().__init__()
        self.creds = YoutubeAuth.authentication()
        self.running = True
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_liked_videos)
        self.check_interval = check_interval * 1000
        self.timer.start(self.check_interval)

    def check_liked_videos(self):
        """Compares liked videos from youtube api to database records. Downloads if missing from DB."""

        # Debugging..
        def list_active_threads():
            print("\nActive Threads:")
            for thread in threading.enumerate():
                print(f"Name: {thread.name}, Alive: {thread.is_alive()}")

        list_active_threads()

        db_manager = DatabaseManager("database.db")
        liked_videos = fetch_liked_videos(self.creds, 10)
        for v in liked_videos:
            if not db_manager.exists(v["video_id"]):
                self.new_like_signal.emit(f"Adding {v['song_title']} to DB")
                db_manager.insert_song(v)
                self.download_video(v)
        self.new_like_signal.emit("Done with this sync run.")

    def download_video(self, v):
        downloader_instance = DownloadWorker(None)
        output_path = downloader_instance.get_output_path(v["artist"], v["song_title"])
        self.new_like_signal.emit(f"Sync Downloading: {v['song_title']}")
        downloader_instance.download_video_with_retries(
            v["video_id"], output_path, v["song_title"]
        )

    def stop(self):
        self.timer.stop()
