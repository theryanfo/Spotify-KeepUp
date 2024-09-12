from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv, dotenv_values
import os
import time

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'RyansCookie'
TOKEN_INFO = "token_info"


@app.route('/')
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
    return redirect(url_for('getTracks', _external=True))


@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    all_songs = []
    i = 0
    while True:
        items = sp.current_user_saved_tracks(limit=50, offset=50 * i)['items']
        i += 1
        all_songs += items
        if (len(items) < 50):
            break
    # return all_songs
    return redirect(url_for('playlists', _external=True))

@app.route('/playlists')
def playlists():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    print(sp)
    items = sp.current_user_playlists(limit=50, offset=0)['items']
    res = []
    for item in items:
        res.append(item['name'])
    return res
    


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=url_for('redirectPage', _external=True),
        scope="user-library-read,playlist-read-private,playlist-read-collaborative"
    )

if __name__ == "__main__":
    app.run(debug=True)
