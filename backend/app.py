from db import update_artists_to_use, update_top_tracks, get_artists_to_use, get_top_tracks
from flask import Flask, request, url_for, session, redirect, jsonify
from flask_session import Session
import spotipy
from flask_cors import CORS
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv, dotenv_values
import os
import time
import random

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.secret_key = os.getenv("SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session-info'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_TYPE'] = 'filesystem'  
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False
Session(app)
TOKEN_INFO = "token_info"


# app routes

@app.route('/')
def index():
    return 'homepage'


@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/is_logged_in')
def is_logged_in():
    print(session)
    if (TOKEN_INFO in session):
        print("logged_in: True")
        return jsonify({"logged_in": True})
    print("logged_in: False")
    return jsonify({"logged_in": False})


@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    # session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    print(session)
    # return redirect(url_for('artistsYouLike', _external=True))
    return redirect('http://localhost:5173/')



@app.route('/artistsYouLike')
def artistsYouLike():
    try:
        token_info = get_token()
    except:
        print("USER NOT LOGGED IN")
        return redirect("/login")
    
    sp = spotipy.Spotify(auth=token_info['access_token'])

    user_id = sp.current_user()['id']

    # get artists from current user top tracks
    trendingArtists = set()
    for track in sp.current_user_top_tracks(limit=30, offset=0)['items']:
        for artist in track['artists']:
            trendingArtists.add(artist['id'])

    # get most diff. songs listened to artists all-time and 
    # already-listened to songs (for exclusion)
    topArtists = {}
    topTracks = []
    i = 0
    while True and i < 20:
        tracks = sp.current_user_top_tracks(limit=50, offset=50 * i)['items']
        i += 1
        for track in tracks:
            artists = []
            for artist in track['artists']:
                artists += [(artist['id'], artist['name'])]
                topArtists[artist['id']] = 1 + topArtists.get(artist['id'], 0)

            topTracks += [(track['name'], track['id'], 
                           track['album']['images'][2]['url'], artists)]
            
        if (len(tracks) < 50):
            break

    # get songs from listened-to artists
    topArtists = sorted(topArtists.items(), key=lambda item: item[1], reverse=True)

    # create final artist list (3 steps)
    # 1. up to 5 artists from sample of most-listened to artists
    artistsToUse = set()
    topTenth = len(topArtists) // 10
    if topTenth >= 5:
        for artist in random.sample(topArtists[:topTenth], 5):
            artistsToUse.add(artist[0])
    else:
        artistsToUse.update(artist for artist in topArtists[:5]) 

    # 2. up to 5 artists from recently Liked songs
    startSize = len(artistsToUse)
    items = sp.current_user_saved_tracks(limit=50, offset=0)['items']
    random.shuffle(items)
    for item in items:
        for artist in item['track']['artists']:
            artistsToUse.add(artist['id'])
            if len(artistsToUse) >= startSize + 5:
                break
        if len(artistsToUse) >= startSize + 5:
            break

    # 3. fill rest up to 20 from artists from user current high frequency tracks
    while len(artistsToUse) < 20:
        for track in topTracks:
            for artist in track[3]:
                artistsToUse.add(artist[0])
                if len(artistsToUse) >= 20:
                    break
            if len(artistsToUse) >= 20:
                break
    
    artists_to_use = list(artistsToUse) 

    # Store artistsToUse and topTracks in MongoDB
    # update_artists_to_use(user_id, artists_to_use)
    # update_top_tracks(user_id, topTracks)
    
    return jsonify(artists_to_use)


@app.route('/getFollowed') # todo
def getFollowed():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/login")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    followed = []
    after_val = None
    i = 0
    while True:
        artists = sp.current_user_followed_artists(limit=50, after=after_val)['artists']
        after_val = artists['cursors']['after']
        followed += artists['items']
        i += 1
        if len(artists['items']) < 50:
            break
    return jsonify(followed)


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
    

# helper functions

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
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    # sp_oauth = create_spotify_oauth()
    # token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    print("TOKEN GOT")
    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=url_for('redirectPage', _external=True),
        scope="user-library-read,user-top-read,user-follow-read,playlist-read-private,playlist-read-collaborative,playlist-modify-public,playlist-modify-private"
    )

# start application

if __name__ == "__main__":
    #app.run(debug=True, use_reloader=False)
    app.run(debug=True)
