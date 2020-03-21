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
    provider = MusicProvider()
    library = provider.music()
    player = MusicPlayer()
    server = Server(player, library)

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
