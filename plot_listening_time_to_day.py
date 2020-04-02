#!/usr/bin/python3
import matplotlib.pyplot as plt
from music_daemon.db import MusicProvider
from datetime import datetime

plt.style.use(['dark_background'])

def next_hour(time):
    return time + 3600 * 1000

if __name__ == '__main__':
    provider = MusicProvider()
    provider.load_music()
    first_time_listening = provider.playbacks[1].time_started

    hours_cnt = 24*6
    times_listened = []

    from_time = first_time_listening
    to_time = next_hour(from_time)
    for i in range(hours_cnt):
        total_time_listened = 0
        for song in provider.get_songs_list():
            total_time_listened += song.time_listened(from_time, to_time)
        total_time_listened / 1000
        times_listened.append(total_time_listened)
        from_time = to_time
        to_time = next_hour(from_time)

    print(times_listened)

    fig, ax = plt.subplots()
    ax.plot([hour_num for hour_num in range(hours_cnt)],
            [time_listened / 1000 for time_listened in times_listened])
    ax.set_xlabel('hour', fontsize=30)
    ax.set_ylabel('seconds listened', fontsize=30)
    fig.suptitle('plot mapping hours to seconds listened', fontsize=30)
    plt.show()
