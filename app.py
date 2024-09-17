from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv, dotenv_values
import os
import time
import random

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session-cookie'
TOKEN_INFO = "token_info"


@app.route('/')
def index():
    return 'homepage'


@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('artistsYouLike', _external=True))


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/artistsYouLike')
def artistsYouLike():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/login")
    
    sp = spotipy.Spotify(auth=token_info['access_token'])

    #topArtists = []
    topTracks = []
    i = 0
    while True:
        tracks = sp.current_user_top_tracks(limit=50, offset=50 * i)['items']
        i += 1
        for track in tracks:
            artists = []
            for artist in track['artists']:
                artists += [(artist['name'], artist['id'])]
            topTracks += [(track['name'], track['id'], track['album']['images'][2]['url'], artists)]
        if (len(tracks) < 50):
            break
    return topTracks


@app.route('/getTracks/<playlist>') # Update to get tracks for selected playlist
def getTracks(playlist):
    if playlist == "Liked":
        return getLiked()
    return 'todo'


@app.route('/getPlaylists')
def getPlaylists():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/login")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    playlists_data = []
    playlists = ["Liked Songs"]
    i = 0
    while True:
        items = sp.current_user_playlists(limit=50, offset=50 * i)['items']
        playlists_data += items
        i += 1
        for item in items:
            playlists.append(item['name'])
        if (len(items) < 50):
            break
    return playlists_data
    

def getLiked():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/login")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    all_songs = []
    i = 0
    while True:
        items = sp.current_user_saved_tracks(limit=50, offset=50 * i)['items']
        i += 1
        all_songs += items
        if (len(items) < 50):
            break
    return all_songs


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    # now = int(time.time())
    # is_expired = token_info['expires_at'] - now < 60
    # if (is_expired):
    #     sp_oauth = create_spotify_oauth()
    #     token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    sp_oauth = create_spotify_oauth()
    token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=url_for('redirectPage', _external=True),
        scope="user-library-read,user-top-read,playlist-read-private,playlist-read-collaborative"
    )

if __name__ == "__main__":
    app.run(debug=True)
