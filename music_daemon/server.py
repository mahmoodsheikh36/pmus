import socket

class Server:
    def __init__(self, music_player, music_library, port=5150):
        self.music_player = music_player
        self.music_library = music_library
        self.socket = None
        self.terminated = False
        self.port = port

    def start(self):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen()
        while True:
            if self.terminated:
                return
            client_socket, addr = self.socket.accept()
            message = client_socket.recv(1024)
            #try:
            response = self.handle_message(message.decode())
            #except Exception as e:
            #    response = 'error handling message'
            client_socket.sendall(response.encode())
            client_socket.close()

    def terminate(self):
        print('terminating server')
        self.terminated = True
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def handle_message(self, msg):
        msg = msg.lower()
        split_by_space = msg.split(' ')
        cmd = split_by_space[0]
        args = split_by_space[1:]

        if cmd == 'pause':
            self.music_player.pause()
        elif cmd == 'resume':
            self.music_player.resume()
        elif cmd == 'play':
            music_object_type = args[0]
            if music_object_type == 'song':
                if len(args[1:]) == 0:
                    return 'please provide song ids'
                song_ids = [int(song_id) for song_id in args[1:]]
                songs = [self.music_library.get_song(song_id)
                         for song_id in song_ids]
                self.music_player.play_clear_queue(songs[0])
                for song in songs[1:]:
                    self.music_player.add_to_queue(song)
            elif music_object_type == 'album':
                if len(args[1:]) == 0:
                    return 'please provide the album\'s id'
                album_id = int(args[1])
                album = self.music_library.get_album(album_id)
                self.music_player.play_album(album)
            else:
                return 'wrong music object type, allowed types: song, album'
        elif cmd == 'next' or cmd == 'next':
            self.music_player.skip_to_next()
        elif cmd == 'prev':
            self.music_player.skip_to_prev()
        elif cmd == 'seek':
            position_in_seconds = int(args[0])
            self.music_player.seek(position_in_seconds)
        elif cmd == 'list':
            music_object_type = args[0]
            if music_object_type == 'song':
                songs_txt = ''
                for song in self.music_library.songs:
                    songs_txt += '{} {} - {}\n'.format(song.id,
                                                       song.name,
                                                       song.artists[0].name)
                return songs_txt
            elif music_object_type == 'album':
                albums_txt = ''
                for album in self.music_library.albums:
                    albums_txt += '{} {} - {}\n'.format(album.id,
                                                        album.name,
                                                        album.artists[0].name)
                return albums_txt
            else:
                return 'wrong music object type, allowed types: song, album'
        elif cmd == 'progress':
            if not self.music_player.current_song():
                return ''
            return '{}/{}'.format(
                    format(self.music_player.progress, '.2f'),
                    format(self.music_player.current_song().duration, '.2f'))
        elif cmd == 'current':
            if not self.music_player.current_song():
                return ''
            song = self.music_player.current_song()
            return '{} {} - {}'.format(song.id,
                                       song.name,
                                       song.artists[0].name)
        elif cmd == 'add':
            music_object_type = args[0]
            if music_object_type == 'song':
                song_ids = [int(song_id) for song_id in args[1:]]
                songs = [self.music_library.get_song(song_id)
                         for song_id in song_ids]
                for song in songs:
                    self.music_player.add_to_queue(song)
            elif music_object_type == 'album':
                return 'not added yet'
            else:
                return 'wrong music object type, allowed types: song, album'
        elif cmd == 'queue':
            queue_txt = ''
            for song in reversed(self.music_player.song_queue):
                queue_txt += '{} {} - {}\n'.format(song.id,
                                                   song.name,
                                                   song.artists[0].name)
            for song in reversed(self.music_player.ended_song_queue):
                queue_txt += '{} {} - {}\n'.format(song.id,
                                                   song.name,
                                                   song.artists[0].name)
            return queue_txt
        elif cmd == 'liked':
                songs_txt = ''
                for song in self.music_library.songs:
                    if not song.is_liked:
                        continue
                    songs_txt += '{} {} - {}\n'.format(song.id,
                                                       song.name,
                                                       song.artists[0].name)
                return songs_txt
        else:
            return 'unknown command'
        return 'OK'
