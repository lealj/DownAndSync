from auth import YoutubeAuth


def fetch_liked_videos(youtube_creds, limit=5):
    if not youtube_creds:
        raise ValueError("YouTube credentials not set.")
    return fetch_liked_videos(youtube_creds, limit)


def insert_liked_videos(videos):
    youtube_api.insert_liked_videos(videos)
