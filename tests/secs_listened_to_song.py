#!/usr/bin/python3
import sys
sys.path.insert(1, '../pmus/')

from pmus.db import MusicProvider

SONG_ID = 23

if __name__ == '__main__':
    provider = MusicProvider()
    print(provider.get_seconds_listened_to_track(SONG_ID))
