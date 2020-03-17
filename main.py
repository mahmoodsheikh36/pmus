import sys
from player import MusicPlayer
from db import MusicProvider

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('enter audio file path as first argument')
        exit(1)
    provider = MusicProvider()
    songs, albums, singles, artists = provider.music()
    print(songs[0].name)
    player = MusicPlayer()
    #x = threading.Thread(target=another_thread_func, args=(player,))
    #x.start()
    #x.join()
    player.play_file(sys.argv[1])
    player.terminate()
