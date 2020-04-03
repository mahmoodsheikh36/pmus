#!/usr/bin/python3
import matplotlib.pyplot as plt
from music_daemon.db import MusicProvider
from datetime import datetime
from music_daemon.utils import current_time

plt.style.use(['dark_background'])

def next_hour(time):
    return time + 3600 * 1000

if __name__ == '__main__':
    provider = MusicProvider()
    provider.load_music()
    first_listen_time = provider.playbacks[1].time_started

    hours_cnt = int((current_time() - first_listen_time) / 1000 / 3600)
    times_listened = []

    from_time = first_listen_time
    to_time = next_hour(from_time)
    for i in range(hours_cnt):
        total_time_listened = 0
        for song in provider.get_songs_list():
            total_time_listened += song.time_listened(from_time, to_time)
        times_listened.append(total_time_listened)
        from_time = to_time
        to_time = next_hour(from_time)

    fig, ax = plt.subplots()
    ax.plot([hour_num for hour_num in range(hours_cnt)],
            [time_listened / 1000 for time_listened in times_listened], 'o-')
    ax.set_xlabel('hour', fontsize=30)
    ax.set_ylabel('seconds listened', fontsize=30)
    fig.suptitle('seconds listened to music in each of\nthe past {} hours'.format(hours_cnt), fontsize=30)
    plt.show()
