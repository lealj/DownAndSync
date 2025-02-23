from .api_auth import YoutubeAuth
from googleapiclient.discovery import build
from .database import DatabaseManager
from app.utils.utility import regex_cleaners, sanitize_start


def setup_liked_videos():
    creds = YoutubeAuth.authentication()
    liked_videos = fetch_liked_videos(creds)
    insert_liked_videos(liked_videos)


def fetch_liked_videos(creds, maxResults=50) -> list:
    """
    Fetches the user's liked videos using the YouTube Data API, continuing to make requests until all liked videos are fetched.
    """
    try:
        youtube = build("youtube", "v3", credentials=creds)
        liked_videos = []
        next_page_token = None  # Start without a page token

        while True:
            # Make a request to the 'videos' endpoint to fetch liked videos
            request = youtube.videos().list(
                part="snippet,contentDetails",
                myRating="like",
                maxResults=maxResults,
                pageToken=next_page_token,
            )

            response = request.execute()

            # Process the response to extract video details
            for item in response.get("items", []):
                video_id = item["id"]
                video_title = sanitize_start(item["snippet"]["title"])

                # Clean str with regex
                video_title = regex_cleaners(video_title)

                # If video is labed Artist - Song
                if "-" in video_title:
                    title_parts = video_title.split("-")
                    artist = title_parts[
                        0
                    ].strip()  # Doesn't need sanitize start, already done ^
                    song_title = sanitize_start(title_parts[1].strip())
                    liked_videos.append(
                        {
                            "video_id": video_id,
                            "artist": artist,
                            "song_title": song_title,
                        }
                    )
                else:
                    channel_name = item["snippet"]["channelTitle"]
                    # Remove "- Topic" if present
                    if "- Topic" in channel_name:
                        channel_name = sanitize_start(
                            channel_name.replace("- Topic", "").strip()
                        )

                    liked_videos.append(
                        {
                            "video_id": video_id,
                            "artist": channel_name,
                            "song_title": video_title,
                        }
                    )

            # Check if there is a next page to continue fetching
            next_page_token = response.get("nextPageToken")

            # If no more pages, break the loop
            if not next_page_token:
                break

        print(f"Fetched {len(liked_videos)} liked videos.")

        return liked_videos

    except Exception as e:
        print(f"Error fetching liked videos: {e}")
        return False


def insert_liked_videos(liked_videos: list):
    try:
        db_manager = DatabaseManager("database.db")
        db_manager.insert_songs(liked_videos)
        db_manager.close()
    except Exception as e:
        print(f"Error inserting liked videos: {e}")
        return False
