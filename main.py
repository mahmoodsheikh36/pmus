import sys
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
    player.terminate()
