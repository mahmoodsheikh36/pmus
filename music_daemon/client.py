import socket
from music_daemon.config import config

RECV_CHUNK_SIZE = 1024

def send_cmd(cmd, host=config.host, port=config.port):
    if isinstance(cmd, str):
        cmd = cmd.encode()
    s = socket.socket()
    s.connect((host, port))
    s.sendall(cmd)
    data = s.recv(RECV_CHUNK_SIZE)
    while data:
        try:
            print(data.decode(), end='')
            data = s.recv(RECV_CHUNK_SIZE)
        except UnicodeDecodeError:
            data += s.recv(RECV_CHUNK_SIZE)
