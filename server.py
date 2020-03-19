import socket

class Server:
    def __init__(self, port=5150):
        self.socket = None
        self.terminated = False
        self.port = port

    def start(self):
        self.socket = socket.socket()
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen()
        while True:
            if self.terminated:
                return
            client_socket, addr = self.socket.accept()
            message = client_socket.recv(1024)
            client_socket.send(self.handle_message(message).encode())
            client_socket.close()

    def terminate(self):
        self.terminated = True
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def handle_message(self, message):
        print(message)
        return 'OK'
