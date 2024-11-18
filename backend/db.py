import os
from dotenv import load_dotenv, dotenv_values
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

uri = ("mongodb+srv://" + os.getenv("MONGODB_USER") + ":" + os.getenv("MONGODB_PASS") + 
       "@spotify-playlist-genera.t7qbu.mongodb.net/?retryWrites=true&w=majority&appName=Spotify-Playlist-Generator")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.spotify_playlist_db

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# database functions

# Function to update artistsToUse
def update_artists_to_use(user_id, artists_to_use):
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"artists": artists_to_use}},
        upsert=True
    )

# Function to update topTracks
def update_top_tracks(user_id, top_tracks):
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"top_tracks": top_tracks}},
        upsert=True
    )

# Function to get artistsToUse
def get_artists_to_use(user_id):
    return db.users.find_one({"user_id": user_id}, {"_id": 0, "artists": 1})

# Function to get topTracks
def get_top_tracks(user_id):
    return db.users.find_one({"user_id": user_id}, {"_id": 0, "top_tracks": 1})


