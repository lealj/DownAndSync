import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Scopes define the access the app needs.
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


class YoutubeAuth:
    def authentication() -> Credentials:
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
            if (
                not creds or not creds.valid
            ):  # If still no valid creds, request new ones
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


class SpotifyAuth:
    CLIENT_ID = "8d13b045cfc3419e8505ccbd81915488"
    CLIENT_SECRET = "48833364bec74252bc623722e3d19297"
    REDIRECT_URI = "http://localhost:8080/callback"
    scope = "user-library-read"

    def authentication(self) -> spotipy.Spotify:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.CLIENT_ID,
                client_secret=self.CLIENT_SECRET,
                redirect_uri=self.REDIRECT_URI,
                scope=self.scope,
            )
        )
        return sp
