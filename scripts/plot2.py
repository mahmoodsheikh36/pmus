#!/usr/bin/python3
import matplotlib.pyplot as plt
from pmus.db import MusicProvider
from datetime import datetime
from pmus.utils import current_time

plt.style.use(['dark_background'])

if __name__ == '__main__':
    provider = MusicProvider()
    provider.load_music()
    first_listen_time = provider.playbacks[1].time_started
    total_time = current_time() - first_listen_time

    time_fraction = 500
    xs = []
    ys = []

    from_time = first_listen_time
    to_time = from_time + total_time / time_fraction
    for i in range(time_fraction):
        time_listened = 0
        for track in provider.get_tracks_list():
            time_listened += track.time_listened(from_time, to_time)
        xs.append(i)
        ys.append(time_listened)
        from_time = to_time
        to_time = from_time + total_time / time_fraction

    fig, ax = plt.subplots()
    ax.plot(xs, ys)
    #ax.set_xlabel('time', fontsize=30)
    #ax.set_ylabel('seconds listened', fontsize=30)
    fig.suptitle('music routine', fontsize=30)
    plt.show()
