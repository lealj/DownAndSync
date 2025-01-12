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
            artist = f"{v['artist']}"
            song_title = f"{v['song_title']}"
            file_name = f"{v['song_title']}.%(ext)s"

            parent_directory = initialize.get_directory_path()
            artist_directory = os.path.join(parent_directory, artist)
            album_directory = os.path.join(artist_directory, song_title)

            os.makedirs(album_directory, exist_ok=True)

            output_path = os.path.join(album_directory, file_name)

            # Check if song already exists in path
            if any(os.path.exists(os.path.join(album_directory, f"{file_name}{ext}")) for ext in ['.mp3', '.m4a', '.webm', '.opus']):
                print(f"File for {v['title']} already exists. Skipping download.")
                continue
            
            print(f"Starting download: {artist} - {song_title}")
            download_video_with_retries(v['video_id'], output_path, song_title)
            time.sleep(5) 
        except Exception as e:
            pass
    print("Download process complete.")


def download_video_with_retries(video_id, output_path, video_title, retries=3, wait=5):
    for attempt in range (0, retries):
        try:
            print(f"Attempt {attempt} to download: {video_title}")
            download_video(video_id, output_path, video_title)
            print(f"Successfully downloaded: {video_title}")
            return
        except Exception as e:
            print(f"Error on attempt {attempt} for {video_title}: {e}")
            if attempt < retries:
                print(f"Retrying in {wait} seconds...")
                time.sleep(wait)
            else:
                print(f"Failed to download {video_title} after {retries} attempts.")


# TODO: Make ffmpeg_location dynamic
def download_video(video_id, output_path, video_title, format='bestaudio'):
    ydl_opts = {
        'format': 'bestaudio[ext!=webm]/best[ext!=webm]',
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': False,
        'extractaudio': True,
        'reject': ['webm'],
        'postprocessors': [
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'},
        ],
        'writethumbnail': True,
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
        import traceback
        error_details = traceback.format_exc()
        print(f"Error downloading video {video_title}: {e}\nDetails: {error_details}")


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