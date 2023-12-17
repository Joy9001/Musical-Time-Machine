from bs4 import BeautifulSoup
import requests
import re
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

CLIENT_ID = os.environ.get("CLIENTID")
CLIENT_SECRET = os.environ.get("CLIENTSECRET")

present_year = datetime.datetime.today().year

date = input("In which date you wanna go? (yyyy-mm-dd): ")

if re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', date) is None:
    print("Invalid Date Format")
    exit(-1)

year = int(date.split("-")[0])
month = int(date.split("-")[1])
day = int(date.split("-")[2])

if year < 1900 or year > present_year:
    print("Year out of bound!")
    exit(-1)
elif month > 12 or month < 1:
    print("Month is out of bound!")
    exit(-1)
elif day > 31 or day < 1:
    print("Day is out of bound")
    exit(-1)

response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}/").text
soup = BeautifulSoup(response, "html.parser")

titles = soup.select(selector="li ul li h3")

song_titles = []
for title in titles:
    t_esc = title.getText()
    song_titles.append(t_esc.replace('\n', '').replace('\t', ''))

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",  # It'll appear automatically when you run the program
        username="Jokeward Billboard Playlist"
    )
)

user_id = sp.current_user()["id"]

song_uris = []

for song in song_titles:
    res = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = res["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard Top 100", public=False,
                                   description="Top 100 Songs from Billboard")

sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
