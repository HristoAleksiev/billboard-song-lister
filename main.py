from bs4 import BeautifulSoup
import requests
import datetime
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint

SPOTIFY_ID = os.getenv("SPOTIFY_ID")
SPOTIFY_KEY = os.getenv("SPOTIFY_KEY")
redirect_URL = "http://example.com"
scope = "playlist-modify-private, playlist-read-private"

spoty = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_ID, client_secret=SPOTIFY_KEY,
                                                  redirect_uri=redirect_URL, scope=scope))
billboard_base_url = "https://www.billboard.com/charts/hot-100/"
billabord_user_selected_url = ""
formatted_date = ""

# Scraping Billboard site for top 100 songs:
while type(formatted_date) == str:
    try:
        user_date = input("Please specify the date to get the top songs from (format must be YYYY-MM-DD): ")
        user_date = user_date.split("-")
        formatted_date = datetime.date(int(user_date[0]), int(user_date[1]), int(user_date[2]))
    except ValueError:
        print("The date you have entered is not in the right format!")
    else:
        billabord_user_selected_url = billboard_base_url + formatted_date.strftime("%Y-%m-%d")

response = requests.get(url=billabord_user_selected_url).text

soup = BeautifulSoup(response, "html.parser")
songs = [{"artist": artist.text, "song_name": song_name.text}
         for artist, song_name
         in zip(soup.find_all(class_="chart-element__information__artist text--truncate color--secondary"),
                soup.find_all(class_="chart-element__information__song text--truncate color--primary"))]

print(songs)

# Searching in Spotify and update songs dict with song URI:
results = spoty.search(q="artist:eminem track:rap god", type="track", market=None)
pprint.pprint(results["tracks"]["items"][0]["uri"])

for song in songs:
    result = spoty.search(q=f"artist:{song['artist']} track:{song['song_name']}", type="track")

    try:
        song.update({"spotify_uri": result["tracks"]["items"][0]["uri"]})
    except IndexError:
        song.update({"spotify_uri": "404 - Not Found!"})

pprint.pprint(songs)


# Creates the playlist in Spotify and adds the songs from top 100:
playlist_name = f"Billboard Top100 - week of: {formatted_date}"
user_existing_playlist = [list["name"] for list in spoty.current_user_playlists()["items"]]
if playlist_name in user_existing_playlist:
    print("Playlist already exists!")
else:
    spoty.user_playlist_create(user=spoty.current_user()["id"], public=False, name=playlist_name)
    print("The Playlist has been created, please check your account!")

playlist_uri = [item["uri"] for item in spoty.current_user_playlists()["items"]
                if item["name"] == playlist_name]

songs_uri_list = [uri["spotify_uri"] for uri in songs if uri["spotify_uri"] != "404 - Not Found!"]
list_for_POST = []
for song in songs_uri_list:
    uri_id = song.split(":")[2]
    list_for_POST.append(uri_id)

spoty.user_playlist_add_tracks(user=spoty.current_user()["id"], playlist_id=playlist_uri[0], tracks=list_for_POST)

pprint.pprint(list_for_POST)
