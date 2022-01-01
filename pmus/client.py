import socket
from pmus.config import config

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
            yield data.decode()
            data = s.recv(RECV_CHUNK_SIZE)
        except UnicodeDecodeError:
            data += s.recv(RECV_CHUNK_SIZE)

def send_cmd_wait_all(cmd, host=config.host, port=config.port):
    all_data = ''
    for data in send_cmd(cmd, host, port):
        all_data += data
    return all_data

def cmd_to_stdout(cmd, host=config.host, port=config.port):
    for data in send_cmd(cmd, host, port):
        print(data, end='', flush=True)
