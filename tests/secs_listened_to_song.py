#!/bin/python
import sys
sys.path.insert(1, '../music_daemon/')

from music_daemon.db import MusicProvider

SONG_ID = 1032

if __name__ == '__main__':
    provider = MusicProvider()
    print(provider.get_seconds_listened_to_song(SONG_ID))