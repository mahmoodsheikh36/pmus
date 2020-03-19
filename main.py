import sys
import time
from player import MusicPlayer
from db import MusicProvider

if __name__ == '__main__':
    provider = MusicProvider()
    songs, albums, singles, artists = provider.music()
    for album in albums:
        print(album.name)
    player = MusicPlayer()
    #x = threading.Thread(target=another_thread_func, args=(player,))
    #x.start()
    #x.join()
    player.play(albums[0].songs[0])
    player.add_to_queue(albums[0].songs[1])
    try:
        time.sleep(3)
        player.skipToNext()
        time.sleep(3)
    except KeyboardInterrupt:
        print('Interrupted')

    player.terminate()
