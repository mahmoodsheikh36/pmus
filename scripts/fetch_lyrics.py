#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

import music_daemon.db # the music daemon/player i wrote
music_provider = music_daemon.db.MusicProvider()

# max connections/threads that can run at a time, 200 might be alot
CONCURRENT_WORKERS = 200

def get_lyrics(song):
    song_name, artist_name = song.name, song.artists[0].name
    url = "https://genius.com/{}-{}-lyrics".format(
            artist_name.replace("'", "").replace(' ', '-').capitalize(),
            song_name.replace("'", "").replace(' ', '-'))
    bs = BeautifulSoup(requests.get(url).content.decode(), 'html.parser')
    lyrics = bs.find_all("div", {"class": "lyrics"})[0].find_all('p')[0].text
    on_lyrics(song, lyrics)

def on_lyrics(song, lyrics):
    music_provider.db_provider.set_song_lyrics(song.id, lyrics)
    print('got lyrics for {} - {}'.format(song.name, song.artists[0].name))

if __name__ == '__main__':
    music_provider.load_music()

    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        for song in music_provider.get_songs_list():
            if music_provider.db_provider.get_song_lyrics(song.id) is None:
                executor.submit(get_lyrics, song)

    print('done, saving to database')
    music_provider.db_provider.commit()
