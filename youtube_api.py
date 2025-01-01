import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Scopes define the access the app needs.
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def youtube_authentication():
    """
    Handles YouTube OAuth 2.0 authentication.
    """
    # Path to store token.json (saved credentials)
    token_file = 'token.json'

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
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
                print("Token successfully refreshed")
            except Exception as e:
                print(f"Error refreshing token: {e}")
        if not creds or not creds.valid:  # If still no valid creds, request new ones
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES
                )
                creds = flow.run_local_server(port=0)
                # Save the new credentials to token.json
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
                print("New credentials generated and saved.")
            except Exception as e:
                print(f"Error during authorization: {e}")
    return creds


# More efficient way to manage liked videos
def fetch_liked_videos(creds, output_file='liked_videos.json'):
    """
    Fetches the user's liked videos using the YouTube Data API, continuing to make requests until all liked videos are fetched.
    """
    try:
        youtube = build('youtube', 'v3', credentials=creds)
        liked_videos = []
        next_page_token = None  # Start without a page token
        
        # while True:
        # Make a request to the 'videos' endpoint to fetch liked videos
        request = youtube.videos().list(
            part="snippet,contentDetails",
            myRating="like",  # Fetch liked videos
            maxResults=5,     # Maximum results per request
            pageToken=next_page_token  # Use the next page token if it exists
        )
        
        response = request.execute()
        
        # Process the response to extract video details
        for item in response.get('items', []):
            video_id = item['id']
            title = item['snippet']['title']
            liked_videos.append({
                "video_id": video_id,
                "title": title
            })
    
        # Check if there is a next page to continue fetching
        #    next_page_token = response.get('nextPageToken')
        
            # If no more pages, break the loop 
        #    if not next_page_token:
        #        break
        
        with open(output_file, 'w') as json_file:
            json.dump(liked_videos, json_file, indent=4)

        print(f"Fetched {len(liked_videos)} liked videos.")

        return liked_videos
    
    except Exception as e:
        print(f"Error fetching liked videos: {e}")
        return []

