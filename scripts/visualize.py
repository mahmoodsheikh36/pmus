#!/usr/bin/python3
import matplotlib.pyplot as plt
from pmus.db import MusicProvider

plt.style.use(['dark_background'])

ENTRY_COUNT = 8

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

def get_top_tracks(provider, limit):
    def compare(track1, track2):
        if track1.time_listened() > track2.time_listened():
            return True
        return False
    return get_largest_elements(provider.get_tracks_list(),
            limit,
            compare)

def get_top_albums(provider, limit):
    def compare(album1, album2):
        if album1.time_listened() > album2.time_listened():
            return True
        return False
    return get_largest_elements(provider.get_albums_list(),
            limit,
            compare)

def get_top_artists(provider, limit):
    def compare(artist1, artist2):
        if artist1.time_listened() > artist2.time_listened():
            return True
        return False
    return get_largest_elements(provider.get_artists_list(),
            limit,
            compare)

if __name__ == '__main__':
    provider = MusicProvider()
    provider.load_music()

    top_albums = get_top_albums(provider, ENTRY_COUNT)
    top_tracks = get_top_tracks(provider, ENTRY_COUNT)
    top_artists = get_top_artists(provider, ENTRY_COUNT)

    fig, (tracks_ax, albums_ax, artists_ax) = plt.subplots(3)
    fig.tight_layout()
    plt.subplots_adjust(hspace=0.5)

    # plot tracks
    #tracks_graph_color = (0.9, 0.4, 0.6)
    tracks_ax.bar(['{}\n{}'.format(track.name, track.artists[0].name)
                     for track in top_tracks],
                    [track.time_listened() / 1000 for track in top_tracks],)
                    #color=tracks_graph_color)
    tracks_ax.set_xlabel('tracks', fontsize=18, #color=tracks_graph_color,
                            weight='bold')
    #tracks_graph.set_ylabel('seconds listened', fontsize=18, #color=tracks_graph_color,
                            #weight='bold')

    # plot albums
    albums_graph_color = (0.5, 0.5, 0.4)
    albums_ax.bar(['{}\n{}'.format(album.name, album.artists[0].name)
                      for album in top_albums],
                     [album.time_listened() / 1000 for album in top_albums],)
                     #color=albums_graph_color)
    albums_ax.set_xlabel('albums', fontsize=18, #color=albums_graph_color,
                            weight='bold')
    #albums_graph.set_ylabel('seconds listened', fontsize=18, #color=albums_graph_color,
    #                        weight='bold')

    # plot artists
    artists_graph_color=(0.3, 0.3, 0.9)
    artists_ax.bar([artist.name for artist in top_artists],
                      [artist.time_listened() / 1000 for artist in top_artists],)
                      #color=artists_graph_color)
    artists_ax.set_xlabel('artists', fontsize=18, #color=artists_graph_color,
                            weight='bold')
    #artists_graph.set_ylabel('seconds listened', fontsize=18, #color=artists_graph_color,
    #                        weight='bold')

    fig.text(0.03, 0.5, 'seconds listened', ha='center', va='center',
             rotation='vertical', fontsize=24, weight='bold')

    #plt.suptitle('playback data visual representation', fontweight='bold',
    #                        fontsize=25)
    #fig.savefig('figure.png', dpi=1)
    plt.show()
