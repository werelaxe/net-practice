import socket

HOST = '127.0.0.1'
PORT = 31337


def main():
    connection = socket.create_connection((HOST, PORT))
    connection.send(b'194.226.242.1\r\n')
    while True:
        buff = connection.recv(4096).decode()
        if not buff:
            break
        print(buff)


if __name__ == '__main__':
    main()
