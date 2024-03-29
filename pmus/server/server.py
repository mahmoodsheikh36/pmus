import socket
import traceback

from pmus.music.player import MusicPlayerMode
from pmus.utils.config import config
from pmus.music.music import Track, Artist, Album
from pmus.utils.utils import multiple_replace, reversed_if

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
            if music_object_type == 'track':
                if len(args[1:]) == 0:
                    yield 'please provide track ids'
                    return
                track_ids = [int(track_id) for track_id in args[1:]]
                tracks = [self.music_provider.tracks[track_id]
                         for track_id in track_ids]
                self.music_player.play_clear_queue(tracks[0])
                for track in tracks[1:]:
                    self.music_player.add_to_queue(track)
            elif music_object_type == 'album':
                if len(args[1:]) == 0:
                    yield 'please provide the album\'s id'
                    return
                album_id = int(args[1])
                album = self.music_provider.albums[album_id]
                self.music_player.play_album(album)
            else:
                yield 'wrong music object type, allowed types: track, album'
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
                yield 'you didnt provide the music object type: album, track'
                return
            music_object_type = args[0]
            if music_object_type == 'track' or music_object_type == 'liked':
                list_liked_tracks_only = music_object_type == 'liked'
                tracks_txt = ''
                for track in self.music_provider.get_tracks_list():
                    if list_liked_tracks_only and not track.is_liked():
                        continue
                    yield '{} {} - {} - {}\n'.format(track.id,
                                                     track.name,
                                                     track.album.name,
                                                     track.artists[0].name)
            elif music_object_type == 'album':
                # if the album id is given we list it's tracks
                # else we list all the albums
                if len(args) > 1:
                    album_id = int(args[1])
                    album = self.music_provider.albums[album_id]
                    if album is None:
                        yield ''
                        return
                    for track in album.tracks:
                        yield '{} {} - {}\n'.format(track.id,
                                                    track.name,
                                                    track.artists[0].name)
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
                yield 'wrong music object type, allowed types: track, album'
                return
        elif cmd == 'progress':
            if not self.music_player.current_track():
                yield ''
                return
            yield '{}/{}'.format(
                    format(self.music_player.progress, '.2f'),
                    format(self.music_player.current_track().duration, '.2f'))
            return
        elif cmd == 'current':
            if not self.music_player.current_track():
                yield ''
                return
            track = self.music_player.current_track()
            yield '{} {} - {}'.format(track.id,
                                      track.name,
                                      track.artists[0].name)
            return
        elif cmd == 'add':
            music_object_type = args[0]
            if music_object_type == 'track':
                track_ids = [int(track_id) for track_id in args[1:]]
                tracks = [self.music_provider.tracks[track_id]
                         for track_id in track_ids]
                for track in tracks:
                    self.music_player.add_to_queue(track)
            elif music_object_type == 'album':
                yield 'not added yet'
                return
            else:
                yield 'wrong music object type, allowed types: track, album'
                return
        elif cmd == 'queue':
            queue_txt = ''
            for track in reversed(self.music_player.track_queue):
                yield '{} {} - {}\n'.format(track.id,
                                            track.name,
                                            track.artists[0].name)
            for track in reversed(self.music_player.ended_track_queue):
                yield '{} {} - {}\n'.format(track.id,
                                            track.name,
                                            track.artists[0].name)
            return
        elif cmd == 'like':
            if len(args) == 0:
                yield 'you didnt provide the tracks id'
                return
            track_id = int(args[0])
            self.music_provider.like_track(self.music_provider.tracks[track_id])
        elif cmd == 'is_liked':
            if len(args) == 0:
                yield 'you didnt provide the id of the track'
                return
            track_id = int(args[0])
            yield str(self.music_provider.tracks[track_id].is_liked()).lower()
        elif cmd == 'loop_track':
            self.music_player.mode = MusicPlayerMode.LOOP_SONG
        elif cmd == 'loop_queue':
            self.music_player.mode = MusicPlayerMode.LOOP_QUEUE
        elif cmd == 'mode':
            yield self.music_player.mode.name
        elif cmd == 'lyrics':
            if len(args) == 0:
                yield 'you didnt provide the id of the track'
                return
            track_id = args[0]
            lyrics = self.music_provider.db_provider.get_track_lyrics(track_id)
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
        elif cmd == 'info': # info <output_music_type> <specifier> <sort_by> <limit> <fmt>
            output_music_type = args[0]
            specifier = args[1]
            sort_by = args[2]
            reverse = False
            if sort_by.startswith('rev_'):
                reverse = True
                sort_by = sort_by.split('rev_')[1] # get rid of rev_
            limit = int(args[3])
            fmt = 'id name\n'
            if len(args) > 4:
                fmt = ' '.join(args[4:])
            for info in get_info(self, output_music_type, specifier, sort_by,
                                 limit, fmt, reverse):
                yield info
        else:
            yield 'unknown command'
        return

def get_artists_of_tracks(tracks):
    artists = []
    for track in tracks:
        for artist in track.artists:
            if not artist in artists:
                artists.append(artist)
    return artists

def get_albums_of_tracks(tracks):
    albums = []
    for track in tracks:
        if not track.album in albums:
            albums.append(track.album)
    return albums

def sort(music_objects, sort_by):
    if sort_by == 'id':
        return music_objects
    def is_bigger(music_object1, music_object2):
        if sort_by == 'name':
            return music_object1.name < music_object2.name
        if sort_by == 'time_liked':
            return music_object1.time_liked > music_object2.time_liked
        if sort_by == 'idx_in_album':
            return music_object1.index_in_album < music_object2.index_in_album
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

def get_info(server, output_music_type, specifier, sort_by, limit, fmt,
             reverse=False):
    music_objects_map = server.music_provider.tracks
    if output_music_type == 'artist':
        music_objects_map = server.music_provider.artists
    elif output_music_type == 'album':
        music_objects_map = server.music_provider.albums
    if limit <= 0:
        limit = None # [:None] results in all elements be selected in list

    if specifier == 'current' or specifier == 'liked':
        if specifier == 'current':
            desired_tracks = server.music_player.current_tracks()
        else:
            desired_tracks = []
            for track in server.music_provider.tracks.values():
                if track.is_liked():
                    desired_tracks.append(track)
        if output_music_type == 'artist':
            for artist in reversed_if(sort(get_artists_of_tracks(desired_tracks),
                                           sort_by), reverse)[:limit]:
                yield format_info(artist, fmt)
        elif output_music_type == 'album':
            for album in reversed_if(sort(get_albums_of_tracks(desired_tracks),
                                          sort_by), reverse)[:limit]:
                yield format_info(album, fmt)
        else:
            for track in reversed_if(sort(desired_tracks, sort_by),
                                    reverse)[:limit]:
                yield format_info(track, fmt)
    elif specifier == 'all':
        for music_object in reversed_if(sort(list(music_objects_map.values()),
                                             sort_by), reverse)[:limit]:
            yield format_info(music_object, fmt)
    else:
        desired_music_objects = []
        for music_object_specifier in reversed_if(specifier.split(','), reverse):
            if '=' in music_object_specifier:
                input_object_type = music_object_specifier.split('=')[0]
                input_object_id = int(music_object_specifier.split('=')[1])
            else:
                input_object_id = int(music_object_specifier)
                input_object_type = output_music_type
            if input_object_type == 'album':
                album = server.music_provider.albums[input_object_id]
                if output_music_type == 'artist':
                    for artist in album.artists:
                        desired_music_objects.append(artist)
                elif output_music_type == 'track':
                    for track in album.tracks:
                        desired_music_objects.append(track)
                else:
                    desired_music_objects.append(album)
            if input_object_type == 'artist':
                artist = server.music_provider.artists[input_object_id]
                if output_music_type == 'album':
                    for album in artist.albums:
                        desired_music_objects.append(album)
                elif output_music_type == 'track':
                    for album in artist.albums:
                        for track in album.tracks:
                            desired_music_objects.append(track)
                else:
                    desired_music_objects.append(artist)
            if input_object_type == 'track':
                track = server.music_provider.tracks[input_object_id]
                if output_music_type == 'album':
                    desired_music_objects.append(track)
                elif output_music_type == 'artist':
                    for artist in track.artists:
                        desired_music_objects.append(artist)
                else:
                    desired_music_objects.append(track)
        objects_yielded = 0
        for music_obj in reversed_if(sort(desired_music_objects, sort_by),
                                     reverse)[:limit]:
            if limit and objects_yielded == limit:
                break
            yield format_info(music_obj, fmt)
            objects_yielded += 1

def format_info(music_object, fmt):
    if isinstance(music_object, Track):
        return multiple_replace(fmt, # music object is track
                {'artist_name' : music_object.artists[0].name,
                 'album_id' : str(music_object.album.id),
                 'album_name': music_object.album.name,
                 'name': music_object.name,
                 'id': str(music_object.id),
                 'url': music_object.audio_file_path})
    if isinstance(music_object, Album): # music object is album
        return multiple_replace(fmt,
                {'id': str(music_object.id),
                 'artist_name': music_object.artists[0].name,
                 'name': music_object.name,
                 'first_audio_file_path': music_object.tracks[0].audio_file_path})
    if isinstance(music_object, Artist): # music object is artist
        try:
            first_audio_file_path = music_object.albums[0].tracks[0].audio_file_path
        except:
            first_audio_file_path = 'none'
        return multiple_replace(fmt,
                {'id': str(music_object.id),
                 'name': music_object.name,
                 'first_audio_file_path': first_audio_file_path})
