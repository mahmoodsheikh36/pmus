#!/usr/bin/python3
import sys
sys.path.insert(1, '../pmus/')

from pmus.db import MusicProvider

if __name__ == '__main__':
    provider = MusicProvider('/home/mahmooz/music')
    provider.find_music()
