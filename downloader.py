import os
from yt_dlp import YoutubeDL
import initialize
import time
from PyQt6.QtCore import QObject, pyqtSignal
from database import DatabaseManager


class DownloadWorker(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.cancel_download = False

    def run(self):
        db_manager = DatabaseManager("database.db")
        videos = db_manager.fetch_songs()
        db_manager.close()

        for v in videos:
            if self.cancel_download:
                self.progress.emit("Download process canceled.")
                break
            try:
                artist = f"{v['artist']}"
                song_title = f"{v['song_title']}"
                file_name = f"{v['song_title']}.%(ext)s"

                parent_directory = initialize.get_directory_path()
                artist_directory = os.path.join(parent_directory, artist)
                album_directory = os.path.join(artist_directory, song_title)

                os.makedirs(album_directory, exist_ok=True)

                output_path = os.path.join(album_directory, file_name)

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

    def print_video_download_options(self, video_id: str) -> None:
        """
        Testing - prints download options for the video
        """
        ydl_opts = {
            "quiet": True,
            "simulate": True,
            "format": "all",
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                self.progress.emit(
                    f"Available download options for video ID: {video_id}"
                )
                info_dict = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}", download=False
                )
                formats = info_dict.get("formats", [])

                for f in formats:
                    self.progress.emit(
                        f"Format ID: {f['format_id']}, Extension: {f['ext']}, Resolution: {f.get('resolution', 'N/A')}, Note: {f.get('format_note', 'N/A')}"
                    )
        except Exception as e:
            self.progress.emit(
                f"Error fetching download options for video ID {video_id}: {e}"
            )
