#!/bin/python
import matplotlib.pyplot as plt
from music_daemon.db import MusicProvider

ENTRY_COUNT = 5

def init_array(size):
    arr = []
    for i in range(size):
        arr.append(None)
    return arr

def get_top_songs(library, limit):
    top_songs = init_array(limit)
    for song in library.songs:
        for i in range(len(top_songs)):
            if song in top_songs:
                i = len(top_songs) + 1
                continue
            if top_songs[i] is None or\
                    song.seconds_listened > top_songs[i].seconds_listened:
                top_songs[i] = song
    return top_songs

def get_top_albums(library, limit):
    top_albums = init_array(limit)
    for album in library.albums:
        for i in range(len(top_albums)):
            if album in top_albums:
                i = len(top_albums) + 1
                continue
            if top_albums[i] is None or\
                    album.seconds_listened() > top_albums[i].seconds_listened():
                top_albums[i] = album
    return top_albums

def get_top_artists(library, limit):
    top_artists = init_array(limit)
    for artist in library.artists:
        for i in range(len(top_artists)):
            if artist in top_artists:
                i = len(top_artists) + 1
                continue
            if top_artists[i] is None or\
                    artist.seconds_listened() > top_artists[i].seconds_listened():
                top_artists[i] = artist
    return top_artists

if __name__ == '__main__':
    provider = MusicProvider()
    library = provider.music()

    top_albums = get_top_albums(library, ENTRY_COUNT)
    top_songs = get_top_songs(library, ENTRY_COUNT)
    top_artists = get_top_artists(library, ENTRY_COUNT)

    # here starts matplotlib
    #plt.figure(figsize=(1, 1))

    fig, (songs_graph, albums_graph, artists_graph) = plt.subplots(3)
    plt.subplots_adjust(hspace=0.5)

    # plot songs
    songs_graph.bar(['{} - {}'.format(song.name, song.artists[0].name)
                     for song in top_songs],
                    [song.seconds_listened for song in top_songs])
    songs_graph.set(xlabel='songs', ylabel='seconds listened')

    # plot albums
    albums_graph.bar(['{} - {}'.format(album.name, album.artists[0].name)
                      for album in top_albums],
                     [album.seconds_listened() for album in top_albums])
    albums_graph.set(xlabel='albums', ylabel='seconds listened')

    # plot artists
    artists_graph.bar([artist.name for artist in top_artists],
                      [artist.seconds_listened() for artist in top_artists])
    artists_graph.set(xlabel='artists', ylabel='seconds listened')

    plt.suptitle('listening data since 20/3/2020')
    plt.show()
