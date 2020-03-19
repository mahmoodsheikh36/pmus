import sys
import time

from player import MusicPlayer
from db import MusicProvider
from server import Server

if __name__ == '__main__':
    provider = MusicProvider()
    songs, albums, singles, artists = provider.music()
    player = MusicPlayer()
    server = Server()
    #player.play(albums[0].songs[0])
    #player.add_to_queue(albums[0].songs[1])
    
    try:
        server.start()
    except KeyboardInterrupt:
        print('Interrupted')

    server.terminate()
    player.terminate()
