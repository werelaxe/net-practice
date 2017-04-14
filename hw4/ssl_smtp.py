import ssl
import socket
import re
import base64
import sys


HOST = 'smtp.mail.ru'
PORT = 587
SMTP_AUTH_LOGIN = 'throwapple'
SMTP_AUTH_PASS = 'simplepassword'

def read(f):
    ans = ""
    line = f.readline().strip()
    while re.match("\d{3} ", line) == None:
        if not line:
            return 0
        print("S: " + line)
        ans += line + "\n"
        line = f.readline().strip()
    print("S: " + line)
    ans += line + "\n"
    return ans

def write(f, s):
    f.write(s + "\n")
    f.flush()
    print("C: " + s)

def b64(s):
    return(base64.b64encode(s.encode()).decode())

def test_ssl_smtp():
    sock = socket.create_connection((HOST, PORT))
    f = sock.makefile('rw')

    ans = read(f)

    write(f, "ehlo test")
    ans  =  read(f)
    write(f, "starttls")
    ans = read(f)
    sock = ssl.wrap_socket(sock = sock)
    write(f, "auth login")
    ans = read(f)

    write(f, b64(SMTP_AUTH_LOGIN))
    ans = read(f)

    write(f, b64(SMTP_AUTH_PASS))
    ans = read(f)

    write(f, "quit")
    ans = read(f)

if __name__ == "__main__":
    test_ssl_smtp()
