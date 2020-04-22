import socket
import traceback

from pmus.player import MusicPlayerMode
from pmus.config import config
from pmus.music import Song, Artist, Album
from pmus.utils import multiple_replace

class Server:
    def __init__(self, music_player, music_provider, host=config.host,
                 port=config.port):
        self.music_player = music_player
        self.music_provider = music_provider
        self.socket = None
        self.terminated = False
        self.port = port
        self.host = host
        self.finding_music = False

    def start(self):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        while True:
            if self.terminated:
                return
            try:
                client_socket, addr = self.socket.accept()
                message = client_socket.recv(1024)
                try:
                    for line in self.handle_message(message.decode()):
                        client_socket.sendall(line.encode())
                except Exception as e:
                    traceback.print_tb(e.__traceback__)
                    print(e)
                    pass
                client_socket.close()
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)

    def terminate(self):
        print('terminating server')
        self.terminated = True
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.music_player.terminate()
        self.music_provider.db_provider.commit()

    def handle_message(self, msg):
        split_by_space = msg.split(' ')
        cmd = split_by_space[0]
        args = split_by_space[1:]

        if cmd == 'pause':
            self.music_player.pause()
        elif cmd == 'resume':
            self.music_player.resume()
        elif cmd == 'play':
            if len(args) == 0:
                yield 'you didnt provide an id'
                return
            music_object_type = args[0]
            if music_object_type == 'song':
                if len(args[1:]) == 0:
                    yield 'please provide song ids'
                    return
                song_ids = [int(song_id) for song_id in args[1:]]
                songs = [self.music_provider.songs[song_id]
                         for song_id in song_ids]
                self.music_player.play_clear_queue(songs[0])
                for song in songs[1:]:
                    self.music_player.add_to_queue(song)
            elif music_object_type == 'album':
                if len(args[1:]) == 0:
                    yield 'please provide the album\'s id'
                    return
                album_id = int(args[1])
                album = self.music_provider.albums[album_id]
                self.music_player.play_album(album)
            else:
                yield 'wrong music object type, allowed types: song, album'
                return
        elif cmd == 'next' or cmd == 'next':
            self.music_player.skip_to_next()
        elif cmd == 'prev':
            self.music_player.skip_to_prev()
        elif cmd == 'seek':
            position_in_seconds = int(args[0])
            self.music_player.seek(position_in_seconds)
        elif cmd == 'list':
            if len(args) == 0:
                yield 'you didnt provide the music object type: album, song'
                return
            music_object_type = args[0]
            if music_object_type == 'song' or music_object_type == 'liked':
                list_liked_songs_only = music_object_type == 'liked'
                songs_txt = ''
                for song in self.music_provider.get_songs_list():
                    if list_liked_songs_only and not song.is_liked():
                        continue
                    yield '{} {} - {} - {}\n'.format(song.id,
                                                     song.name,
                                                     song.album.name,
                                                     song.artists[0].name)
            elif music_object_type == 'album':
                # if the album id is given we list it's songs
                # else we list all the albums
                if len(args) > 1:
                    album_id = int(args[1])
                    album = self.music_provider.albums[album_id]
                    if album is None:
                        yield ''
                        return
                    for song in album.songs:
                        yield '{} {} - {}\n'.format(song.id,
                                                    song.name,
                                                    song.artists[0].name)
                else:
                    for album in self.music_provider.get_albums_list():
                        yield '{} {} - {}\n'.format(album.id,
                                                    album.name,
                                                    album.artists[0].name)
            elif music_object_type == 'artist':
                if len(args) == 0:
                    yield 'you didnt provide the artist id'
                    return
                for artist in self.music_provider.get_artists_list():
                    yield '{} {}\n'.format(artist.id, artist.name)
            else:
                yield 'wrong music object type, allowed types: song, album'
                return
        elif cmd == 'progress':
            if not self.music_player.current_song():
                yield ''
                return
            yield '{}/{}'.format(
                    format(self.music_player.progress, '.2f'),
                    format(self.music_player.current_song().duration, '.2f'))
            return
        elif cmd == 'current':
            if not self.music_player.current_song():
                yield ''
                return
            song = self.music_player.current_song()
            yield '{} {} - {}'.format(song.id,
                                      song.name,
                                      song.artists[0].name)
            return
        elif cmd == 'add':
            music_object_type = args[0]
            if music_object_type == 'song':
                song_ids = [int(song_id) for song_id in args[1:]]
                songs = [self.music_provider.songs[song_id]
                         for song_id in song_ids]
                for song in songs:
                    self.music_player.add_to_queue(song)
            elif music_object_type == 'album':
                yield 'not added yet'
                return
            else:
                yield 'wrong music object type, allowed types: song, album'
                return
        elif cmd == 'queue':
            queue_txt = ''
            for song in reversed(self.music_player.song_queue):
                yield '{} {} - {}\n'.format(song.id,
                                            song.name,
                                            song.artists[0].name)
            for song in reversed(self.music_player.ended_song_queue):
                yield '{} {} - {}\n'.format(song.id,
                                            song.name,
                                            song.artists[0].name)
            return
        elif cmd == 'like':
            if len(args) == 0:
                yield 'you didnt provide the songs id'
                return
            song_id = int(args[0])
            self.music_provider.like_song(self.music_provider.songs[song_id])
        elif cmd == 'is_liked':
            if len(args) == 0:
                yield 'you didnt provide the id of the song'
                return
            song_id = int(args[0])
            yield str(self.music_provider.songs[song_id].is_liked()).lower()
        elif cmd == 'loop_song':
            self.music_player.mode = MusicPlayerMode.LOOP_SONG
        elif cmd == 'loop_queue':
            self.music_player.mode = MusicPlayerMode.LOOP_QUEUE
        elif cmd == 'mode':
            yield self.music_player.mode.name
        elif cmd == 'lyrics':
            if len(args) == 0:
                yield 'you didnt provide the id of the song'
                return
            song_id = args[0]
            lyrics = self.music_provider.db_provider.get_song_lyrics(song_id)
            if not lyrics:
                yield ''
            else:
                yield lyrics
            return
        elif cmd == 'find_music':
            if self.finding_music:
                yield 'already looking for music, chill'
                return
            self.finding_music = True
            if args:
                self.music_provider.find_music(' '.join(args))
            else:
                self.music_provider.find_music()
            self.music_provider.unload_music()
            self.music_provider.load_music()
            self.finding_music = False
            yield 'done'
        elif cmd == 'info': # info <music_object_type> <specifier> <sort_by> <fmt>
            if not args:
                yield 'you didnt provide the music object type or the ids'
                return
            music_object_type = args[0]
            specifier = args[1]
            sort_by = args[2]
            fmt = 'id name'
            if len(args) > 3:
                fmt = ' '.join(args[3:])
            for info in get_info(self, music_object_type, specifier,
                                 sort_by, fmt):
                yield info
        else:
            yield 'unknown command'
        return

def get_artists_of_songs(songs):
    artists = []
    for song in songs:
        for artist in song.artists:
            if not artist in artists:
                artists.append(artist)
    return artists

def get_albums_of_songs(songs):
    albums = []
    for song in songs:
        if not song.album in albums:
            albums.append(song.album)
    return albums

def sort(music_objects, sort_by):
    if sort_by == 'id':
        return music_objects
    def is_bigger(music_object1, music_object2):
        if sort_by == 'name':
            return music_object1.name < music_object2.name
        if sort_by == 'time_liked':
            return music_object1.time_liked > music_object2.time_liked
    for idx1 in range(len(music_objects)):
        for idx2 in range(len(music_objects)):
            if is_bigger(music_objects[idx1], music_objects[idx2]):
                music_objects[idx1], music_objects[idx2] =\
                        music_objects[idx2], music_objects[idx1]
    """
    we are sorting in-place so returning the list wouldnt make sense
    but it makes for loops easier to type by just doing 'for in sort(list)'
    """
    return music_objects

def get_info(server, music_object_type_str, specifier, sort_by, fmt):
    music_objects_map = server.music_provider.songs
    if music_object_type_str == 'artist':
        music_objects_map = server.music_provider.artists
    elif music_object_type_str == 'album':
        music_objects_map = server.music_provider.albums

    if specifier == 'current' or specifier == 'liked':
        if specifier == 'current':
            desired_songs = server.music_player.current_songs()
        else:
            desired_songs = []
            for song in server.music_provider.songs.values():
                if song.is_liked():
                    desired_songs.append(song)
        if music_object_type_str == 'artist':
            for artist in sort(get_artists_of_songs(desired_songs), sort_by):
                yield format_info(artist, fmt)
        elif music_object_type_str == 'album':
            for album in sort(get_albums_of_songs(desired_songs), sort_by):
                yield format_info(album, fmt)
        else:
            for song in sort(desired_songs, sort_by):
                yield format_info(song, fmt)
    elif specifier == 'all':
        for music_object in sort(list(music_objects_map.values()), sort_by):
            yield format_info(music_object, fmt)
    else: # else its a comma seperated list of ids
        for music_object_id in specifier.split(','):
            yield format_info(music_objects_map[int(music_object_id)], fmt)

def format_info(music_object, fmt):
    if isinstance(music_object, Song):
        return multiple_replace(fmt, # music object is song
                {'artist_name' : music_object.artists[0].name,
                 'album_id' : str(music_object.album.id),
                 'album_name': music_object.album.name,
                 'name': music_object.name,
                 'id': str(music_object.id),
                 'url': music_object.audio_url})
    if isinstance(music_object, Album): # music object is album
        return multiple_replace(fmt,
                {'id': str(music_object.id),
                 'name': music_object.name,
                 'first_audio_url': music_object.songs[0].audio_url,
                 'artist_name': music_object.artists[0].name})
    if isinstance(music_object, Artist): # music object is artist
        try:
            first_audio_url = music_object.albums[0].songs[0].audio_url
        except:
            first_audio_url = 'none'
        return multiple_replace(fmt,
                {'id': str(music_object.id),
                 'name': music_object.name,
                 'first_audio_url': first_audio_url})
