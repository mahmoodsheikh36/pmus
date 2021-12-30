#!/usr/bin/python3
import matplotlib.pyplot as plt
from pmus.db import MusicProvider
from pmus.utils import current_time

plt.style.use(['dark_background'])

if __name__ == '__main__':
    provider = MusicProvider()
    provider.load_music()
    first_listen_time = provider.playbacks[1].time_started
    total_time = current_time() - first_listen_time

    time_fractions = 300
    xs = []
    ys = []

    from_time = first_listen_time
    to_time = from_time + total_time / time_fractions
    time_listened = 0
    for i in range(time_fractions):
        print(i)
        for track in provider.get_tracks_list():
            time_listened += track.time_listened(from_time, to_time)
        xs.append((from_time - first_listen_time) / 1000 / 3600)
        ys.append(time_listened / 1000 / 3600)
        from_time = to_time
        to_time = from_time + total_time / time_fractions

    print('plotting')
    fig, ax = plt.subplots()
    fig.set_size_inches(19.2, 10.6)
    ax.plot(xs, ys)
    ax.tick_params(axis='both', which='major', labelsize=20) 
    ax.set_xlabel('actual hours', fontsize=30)
    ax.set_ylabel('hours spent listening to music', fontsize=30)
    fig.tight_layout()
    plt.show()
