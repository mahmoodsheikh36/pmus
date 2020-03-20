import sys
import time
import traceback

from player import MusicPlayer
from db import MusicProvider
from server import Server

if __name__ == '__main__':
    provider = MusicProvider()
    library = provider.music()
    player = MusicPlayer()
    server = Server(player, library)
    
    try:
        server.start()
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
    except KeyboardInterrupt:
        print('interrupted, terminating..')

    server.terminate()
    player.terminate()
