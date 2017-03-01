from time import sleep
import socket
import threading

HOST = '127.0.0.1'
PORT = 31337
MAX_USERS_COUNT = 256


class MultiuserServer:
    def __init__(self, host, port, max_users_count):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(max_users_count)
        self.sock = sock

    @staticmethod
    def process_user(connection, address):
        print('connection from {}'.format(address))
        connection.sendall(b'hello!\r\n')
        sleep(5)
        connection.sendall(b'bye!\r\n')
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()

    def start(self):
        while True:
            conn, addr = self.sock.accept()
            new_thread = threading.Thread(target=MultiuserServer.process_user, args=(conn, addr))
            new_thread.start()


def main():
    server = MultiuserServer(HOST, PORT, MAX_USERS_COUNT)
    server.start()

if __name__ == '__main__':
    main()
