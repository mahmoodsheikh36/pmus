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
                song_id = int(args[1])
                song = self.music_library.get_song(song_id)
                self.music_player.play(song)
            elif music_object_type == 'album':
                album_id = int(args[1])
                album = self.music_library.get_album(album_id)
                self.music_player.play_album(album)
            else:
                return 'wrong music object type, allowed types: song, album'
        elif cmd == 'skip' or cmd == 'skip_to_next':
            self.music_player.skip_to_next()
        elif cmd == 'skip_to_prev':
            self.music_player.skip_to_prev()
        elif cmd == 'seek':
            position_in_seconds = int(args[0])
            self.music_player.seek(position_in_seconds)
        else:
            return 'unknown command'
        return 'OK'

class Client:
    def __init__(self, port=5150):

