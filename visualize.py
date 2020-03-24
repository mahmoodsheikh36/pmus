#!/usr/bin/python3
import matplotlib.pyplot as plt
from music_daemon.db import MusicProvider

ENTRY_COUNT = 7

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
    songs_graph_color = (0.9, 0.4, 0.6)
    songs_graph.bar(['{}\n{}'.format(song.name, song.artists[0].name)
                     for song in top_songs],
                    [song.seconds_listened for song in top_songs],
                    color=songs_graph_color)
    songs_graph.set_xlabel('songs', fontsize=18, color=songs_graph_color,
                            weight='bold')
    songs_graph.set_ylabel('seconds listened', fontsize=18, color=songs_graph_color,
                            weight='bold')

    # plot albums
    albums_graph_color = (0.5, 0.5, 0.4)
    albums_graph.bar(['{}\n{}'.format(album.name, album.artists[0].name)
                      for album in top_albums],
                     [album.seconds_listened() for album in top_albums],
                     color=albums_graph_color)
    albums_graph.set_xlabel('albums', fontsize=18, color=albums_graph_color,
                            weight='bold')
    albums_graph.set_ylabel('seconds listened', fontsize=18, color=albums_graph_color,
                            weight='bold')

    # plot artists
    artists_graph_color=(0.3, 0.3, 0.9)
    artists_graph.bar([artist.name for artist in top_artists],
                      [artist.seconds_listened() for artist in top_artists],
                      color=artists_graph_color)
    artists_graph.set_xlabel('artists', fontsize=18, color=artists_graph_color,
                            weight='bold')
    artists_graph.set_ylabel('seconds listened', fontsize=18, color=artists_graph_color,
                            weight='bold')

    plt.suptitle('playback data visual representation', fontweight='bold',
                            fontsize=25)
    plt.show()
