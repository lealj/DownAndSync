import os
import tempfile
from yt_dlp import YoutubeDL
import json
import initialize
import time

def download_liked_videos(app):
    videos = load_liked_videos_from_json()

    for v in videos:
        if app.cancel_download:
            print("Download process canceled.")
            break
        try:
            file_name = f"{v['title']}"
            output_path = os.path.join(initialize.get_directory_path(), f"{file_name}.%(ext)s")

            # Check if song already exists in path
            if any(os.path.exists(os.path.join(initialize.get_directory_path(), f"{file_name}{ext}")) for ext in ['.mp3', '.m4a', '.webm', '.opus']):
                print(f"File for {v['title']} already exists. Skipping download.")
                continue

            download_video(v['video_id'], output_path, v['title'])
            # print_video_download_options(v['video_id'])
            time.sleep(5) 
        except Exception as e:
            pass
    print("Download process complete.")


def download_video(video_id, output_path, video_title, format='bestaudio'):
    ydl_opts = {
        'format': 'bestaudio[ext!=webm]/best[ext!=webm]',
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': False,
        'extractaudio': True,
        'reject': ['webm']
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


def print_video_download_options(video_id):
    '''
    Testing - prints download options for the video
    '''
    ydl_opts = {
        'quiet': True,
        'simulate': True,
        'format': 'all',
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Available download options for video ID: {video_id}")
            info_dict = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            formats = info_dict.get('formats', [])
            
            for f in formats:
                print(f"Format ID: {f['format_id']}, Extension: {f['ext']}, Resolution: {f.get('resolution', 'N/A')}, Note: {f.get('format_note', 'N/A')}")
    except Exception as e:
        print(f"Error fetching download options for video ID {video_id}: {e}")