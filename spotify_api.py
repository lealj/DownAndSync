import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Replace these with your Spotify app credentials
CLIENT_ID = "8d13b045cfc3419e8505ccbd81915488"
CLIENT_SECRET = "48833364bec74252bc623722e3d19297"
REDIRECT_URI = "http://localhost:8080/callback"

scope = "user-library-read"

def spotify_authentication():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scope
    ))
    return sp
    
def get_liked_songs(creds, ):
    results = creds.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(f"{track['artists'][0]['name']} - {track['name']}") #idx
