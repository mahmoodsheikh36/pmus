#!/usr/bin/python3
import matplotlib.pyplot as plt
from music_daemon.db import MusicProvider
from music_daemon.utils import current_time
import numpy as np

plt.style.use(['dark_background'])

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
        if song1.time_listened() > song2.time_listened():
            return True
        return False
    print('loaded music')
    return get_largest_elements(provider.get_songs_list(), limit, compare)

if __name__ == '__main__':
    provider = MusicProvider()
    provider.load_music()
    top_songs = get_top_songs(provider, 30)
    print('got top songs')
    top_songs.reverse()

    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(111)
    ax.set_yticks([])

    first_listen_time = provider.playbacks[1].time_started
    total_time = current_time() - first_listen_time

    bar_plot = ax.barh(range(len(top_songs)),
                       [song.time_listened() / 1000 for song in top_songs],
                       color='grey')

    for idx, rect in enumerate(bar_plot):
        ax.text(10, rect.get_y() + rect.get_height() / 3, top_songs[idx].name,
                fontsize=14, color='w')

    fig.tight_layout()
    plt.show()
