from PyQt6.QtCore import QObject, pyqtSignal
from app.core.database import DatabaseManager
import os
import time
from app.core.config import get_directory_path
from yt_dlp import YoutubeDL


class DownloadWorker(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    started = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.cancel_download = False
        self.db_manager = None
        self.directory_path = get_directory_path()

    def run(self):
        self.db_manager = DatabaseManager("database.db")
        videos = self.db_manager.fetch_songs()
        self.db_manager.close()

        for v in videos:
            if self.cancel_download:
                self.progress.emit("Download process canceled.")
                break
            try:
                artist = f"{v['artist']}"
                song_title = f"{v['song_title']}"
                output_path = self.get_output_path(artist, song_title)
                album_directory = os.path.dirname(output_path)

                os.makedirs(album_directory, exist_ok=True)

                # Check if song already exists in path
                if any(
                    os.path.exists(
                        os.path.join(album_directory, f"{v['song_title']}{ext}")
                    )
                    for ext in [".mp3", ".m4a", ".webm", ".opus", ".mp4", ".flac"]
                ):
                    self.progress.emit(
                        f"File for {v['song_title']} already exists. Skipping download."
                    )
                    continue

                self.progress.emit(f"Starting download: {artist} - {song_title}")
                self.download_video_with_retries(v["video_id"], output_path, song_title)
                time.sleep(5)
            except Exception as e:
                pass
        self.progress.emit("Download process complete.")

    def download_video_with_retries(
        self, video_id: str, output_path: str, video_title: str, retries=3, wait=5
    ) -> None:
        for attempt in range(0, retries):
            try:
                self.progress.emit(f"Attempt {attempt} to download: {video_title}")
                self.download_video(video_id, output_path, video_title)
                self.progress.emit(f"Successfully downloaded: {video_title}")
                return
            except Exception as e:
                self.progress.emit(f"Error on attempt {attempt} for {video_title}: {e}")
                if attempt < retries:
                    self.progress.emit(f"Retrying in {wait} seconds...")
                    time.sleep(wait)
                else:
                    self.progress.emit(
                        f"Failed to download {video_title} after {retries} attempts."
                    )

    def download_video(
        self, video_id: str, output_path: str, video_title: str, format="bestaudio"
    ) -> None:
        ydl_opts = {
            "format": "bestaudio[ext!=webm]/best[ext!=webm]",
            "outtmpl": output_path,
            "quiet": True,
            "noplaylist": False,
            "extractaudio": True,
            "reject": ["webm"],
            "postprocessors": [
                {"key": "FFmpegMetadata"},
                {"key": "EmbedThumbnail"},
            ],
            "writethumbnail": True,
            "ffmpeg_location": r"C:\Users\lealj\OneDrive\Documents\GitHub\DownAndSync\ffmpeg\bin",
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
                if result == 0:
                    self.progress.emit(f"{video_title} downloaded successfully.")
                else:
                    self.progress.emit(f"Issue downloading {video_title}.")
        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            self.progress.emit(
                f"Error downloading video {video_title}: {e}\nDetails: {error_details}"
            )

    def get_output_path(self, artist: str, song_title: str) -> str:
        parent_directory = self.directory_path
        artist_directory = os.path.join(parent_directory, artist)
        album_directory = os.path.join(artist_directory, song_title)
        file_name = f"{song_title}.%(ext)s"
        output_path = os.path.join(album_directory, file_name)
        return output_path
