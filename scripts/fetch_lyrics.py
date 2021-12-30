#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

import pmus.db # the music daemon/player i wrote
music_provider = pmus.db.MusicProvider()

# max connections/threads that can run at a time, 200 might be alot
CONCURRENT_WORKERS = 200
CHARS_TO_REMOVE = ".'?!"

def get_lyrics(track):
    track_name, artist_name = track.name, track.artists[0].name
    for char_to_remove in CHARS_TO_REMOVE:
        artist_name = artist_name.replace(char_to_remove, "").replace('/', '-')
        track_name = track_name.replace(char_to_remove, "")
    url = "https://genius.com/{}-{}-lyrics".format(
            artist_name.replace('& ', 'and ').replace(' ', '-').capitalize(),
            track_name.replace('& ', 'and ').replace(' ', '-'))
    bs = BeautifulSoup(requests.get(url).content.decode(), 'html.parser')
    lyrics = bs.find_all("div", {"class": "lyrics"})[0].find_all('p')[0].text
    on_lyrics(track, lyrics)

def on_lyrics(track, lyrics):
    music_provider.db_provider.set_track_lyrics(track.id, lyrics)
    print('got lyrics for {} - {}'.format(track.name, track.artists[0].name))

if __name__ == '__main__':
    print('note that its better to kill the music daemon before running'
           ' this script because this script locks the database')
    music_provider.load_music()

    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        for track in music_provider.get_tracks_list():
            if music_provider.db_provider.get_track_lyrics(track.id) is None:
                executor.submit(get_lyrics, track)

    print('done, saving to database')
    music_provider.db_provider.commit()
