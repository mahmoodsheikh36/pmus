#!/usr/bin/python3
import matplotlib.pyplot as plt
from music_daemon.db import MusicProvider

ENTRY_COUNT = 4

def get_largest_elements(list_to_sort, limit, compare):
    mylist = list_to_sort.copy()
    final_list = []
    for i in range(limit):
        biggest = mylist[0]
        for j in range(len(mylist)):
            element = mylist[j]
            if compare(element, biggest):
                biggest = element
        final_list.append(biggest)
        mylist.remove(biggest)
    return final_list

def get_top_songs(provider, limit):
    def compare(song1, song2):
        if song1.seconds_listened > song2.seconds_listened:
            return True
        return False
    return get_largest_elements(provider.get_songs_list(),
            limit,
            compare)

def get_top_albums(provider, limit):
    def compare(album1, album2):
        if album1.seconds_listened() > album2.seconds_listened():
            return True
        return False
    return get_largest_elements(provider.get_albums_list(),
            limit,
            compare)

def get_top_artists(provider, limit):
    def compare(artist1, artist2):
        if artist1.seconds_listened() > artist2.seconds_listened():
            return True
        return False
    return get_largest_elements(provider.get_artists_list(),
            limit,
            compare)

if __name__ == '__main__':
    provider = MusicProvider()
    provider.load_music()

    top_albums = get_top_albums(provider, ENTRY_COUNT)
    top_songs = get_top_songs(provider, ENTRY_COUNT)
    top_artists = get_top_artists(provider, ENTRY_COUNT)

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
