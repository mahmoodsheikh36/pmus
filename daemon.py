#!/bin/python
import sys
import time
import traceback
import signal
import os

from music_daemon.player import MusicPlayer
from music_daemon.db import MusicProvider
from music_daemon.server import Server

if __name__ == '__main__':
    should_find_music = False
    if len(sys.argv) > 1:
        should_find_music = sys.argv[1]
    provider = MusicProvider('/home/mahmooz/music/')
    if should_find_music == 'true':
        provider.find_music()
        print('done finding music')
    provider.load_music()
    print('loaded music')
    player = MusicPlayer()
    server = Server(player, provider)

    def on_exit(signum=None, frame=None):
        server.terminate()
        player.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)
    
    try:
        server.start()
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
        on_exit()
