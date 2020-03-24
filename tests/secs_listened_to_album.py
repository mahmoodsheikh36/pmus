#!/usr/bin/python3
import sys
sys.path.insert(1, '../music_daemon/')

from music_daemon.db import MusicProvider

album_id = 44

if __name__ == '__main__':
    provider = MusicProvider()
    library = provider.music()
    print(library.get_album(album_id).seconds_listened())
