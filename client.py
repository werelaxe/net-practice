import datetime
from contextlib import closing
from socket import socket, AF_INET, SOCK_DGRAM
import sys
import struct
import datetime
import time


def get_time():
    with closing(socket(AF_INET, SOCK_DGRAM)) as s:
        s.connect(("pool.ntp.org", 123))
        s.send(struct.pack("BBBBLLLLL", 35, 0, 0, 0, 0, 0, 0, 0, 0))
        data = s.recv(2048)
        data = data[40:44]
        net_time = struct.unpack("!L", data)
        return net_time

c_time = get_time()[0] - 2208988800

print(datetime.datetime.fromtimestamp(c_time))
