import os
import tempfile
from yt_dlp import YoutubeDL
import json
import initialize
import time

def download_liked_videos():
    videos = load_liked_videos_from_json()

    for v in videos:
        try:
            file_name = f"{v['title']}"
            output_path = os.path.join(initialize.get_directory_path(), f"{file_name}.%(ext)s")

            # Check if song already exists in path
            if any(os.path.exists(os.path.join(initialize.get_directory_path(), f"{file_name}{ext}")) for ext in ['.mp3', '.m4a', '.webm', '.opus']):
                print(f"File for {v['title']} already exists. Skipping download.")
                continue

            download_video(v['video_id'], output_path, v['title'])
            time.sleep(5) 
        except Exception as e:
            pass


def download_video(video_id, output_path, video_title, format='bestaudio'):
    ydl_opts = {
        'format': 'bestaudio[ext!=webm]/best[ext!=webm]',
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': True,
        'extractaudio': True,
        'reject': ['webm'],
        'postprocessors': [
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'},
        ],
        'ffmpeg_location': r'C:\Users\lealj\OneDrive\Documents\GitHub\DownAndSync\ffmpeg\bin'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
            if result == 0:
                print(f"{video_title} downloaded successfully.")
            else:
                print(f"Issue downloading {video_title}.")
    except Exception as e:
        print(f"Error downloading video {video_title}: {e}")


def load_liked_videos_from_json(file_path='liked_videos.json'):
    """
    Loads the liked videos from a JSON file into a Python data structure (list).
    """
    try:
        with open(file_path, 'r') as json_file:
            liked_videos = json.load(json_file)
        print(f"Loaded {len(liked_videos)} liked videos from {file_path}.")
        return liked_videos
    
    except Exception as e:
        print(f"Error loading liked videos: {e}")
        return []

