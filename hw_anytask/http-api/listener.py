import socket
import time

with open("response.html", "r") as file:
    page = file.read()

header = """HTTP/1.0 200 OK\r
Server: SimpleHTTP/0.6 Python/3.5.2\r
Content-type: text/html; charset=utf-8\r
Content-Length: {}\r
\r
""".format(len(page)).encode()

BUFFER_SIZE = 10240


def start_auth_server(pipe_end):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_socket:  # connection for send page
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(("127.0.0.1", 0))
        port = listen_socket.getsockname()[1]
        pipe_end.send(port)
        listen_socket.listen(1)
        sock, addr = listen_socket.accept()
        sock.recv(BUFFER_SIZE)
        sock.send(header + (page.replace("PORT", str(port))).encode())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_socket:  # connection for receive token
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(("127.0.0.1", port))
        listen_socket.listen(1)
        sock, addr = listen_socket.accept()  # connection for send page
        data = sock.recv(BUFFER_SIZE)
        pipe_end.send(data.decode())
