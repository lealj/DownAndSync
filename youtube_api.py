import os
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import json
from database import DatabaseManager

# Scopes define the access the app needs.
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


def youtube_authentication() -> Credentials:
    """
    Handles YouTube OAuth 2.0 authentication.
    """
    # Path to store token.json (saved credentials)
    token_file = "token.json"

    creds = None

    # Check if token.json exists (to reuse credentials)
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        print("Credentials retrieved.")

    # If no valid credentials, request new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(token_file, "w") as token:
                    token.write(creds.to_json())
                print("Token successfully refreshed")
            except Exception as e:
                print(f"Error refreshing token: {e}")
        if not creds or not creds.valid:  # If still no valid creds, request new ones
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
                # Save the new credentials to token.json
                with open(token_file, "w") as token:
                    token.write(creds.to_json())
                print("New credentials generated and saved.")
            except Exception as e:
                print(f"Error during authorization: {e}")
    return creds


# More efficient way to manage liked videos
def fetch_liked_videos(creds) -> bool:
    """
    Fetches the user's liked videos using the YouTube Data API, continuing to make requests until all liked videos are fetched.
    """

    def sanitize_start(value: str) -> str:
        """
        Santize song title and artist name, so that they don't start with invalid characters.
        For creating files later without error.
        """
        INVALID_CHARS = set('<>:"/\\|?*.')
        while value and value[0] in INVALID_CHARS:
            value = value[1:]
        return value

    def regex_cleaners(video_title: str) -> str:
        # Remove parenthesis substr ie (Official music vid)
        if "(" in video_title and ")" in video_title:
            video_title = re.sub(r"\s?\(.*?\)", "", video_title)

        # Remove brackets
        if "[" in video_title and "]" in video_title:
            video_title = re.sub(r"\s?\[.*?\]", "", video_title)

        # Remove numbered songs
        if video_title[0].isdigit() and "." in video_title:
            video_title = re.sub(r"^\d+\.\s?", "", video_title)

        return video_title

    try:
        youtube = build("youtube", "v3", credentials=creds)
        liked_videos = []
        next_page_token = None  # Start without a page token

        # while True:
        # Make a request to the 'videos' endpoint to fetch liked videos
        request = youtube.videos().list(
            part="snippet,contentDetails",
            myRating="like",
            maxResults=5,
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

        # next_page_token = response.get("nextPageToken")

        # If no more pages, break the loop
        # if not next_page_token:
        #    break
        db_manager = DatabaseManager("database.db")
        db_manager.insert_songs(liked_videos)
        db_manager.close()

        print(f"Fetched {len(liked_videos)} liked videos.")

        return True

    except Exception as e:
        print(f"Error fetching liked videos: {e}")
        return False
