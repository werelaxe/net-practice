#!/usr/bin/python3

import traceback
from concurrent.futures import ThreadPoolExecutor
import socket
import struct
import binascii

import time

DNS_DEFAULT_PORT = 53
PORT = DNS_DEFAULT_PORT
BUFFER_SIZE = 64 * 1024
MAX_WORKERS = 256
QNAME_CODES = {1: "A", 2: "NS", 5: "CNAME", 12: "PTR", 13: "HINFO", 15: "MX", 252: "AXFR", 255: "ANY"}
QCLASS_CODES = {1: "IN"}


def get_mask_val(data, mask: str) -> int:
    if len(mask) != 8:
        raise Exception
    return data & int(mask, 2)


def nice_hex(data):
    return b" ".join(binascii.hexlify(data)[index * 2:index * 2 + 2] for index in range(len(data) // 2 + 1))


class DNSPacket:
    def from_bytes(self, data, transport_protocol):
        # print(nice_hex(data))
        if transport_protocol.lower() == "tcp":
            self.message_len = struct.unpack("!H", data[:2])
            data = data[2:]
        elif transport_protocol.lower() != "udp":
            raise ValueError("Unexpected protocol type: {}".format(transport_protocol))
        self.id = struct.unpack("!H", data[:2])
        left_options = data[2]
        right_options = data[3]
        # print(bin(left_options)[2:].zfill(8))
        self.qr = get_mask_val(left_options,                   "10000000")
        self.opcode = get_mask_val(left_options,               "01111000")
        self.authoritative_answer = get_mask_val(left_options, "00000100")
        self.turncation = get_mask_val(left_options,           "00000010")
        self.recursion_desired = get_mask_val(left_options,    "00000001")
        self.recursion_available = get_mask_val(right_options,         "10000000")
        _ = get_mask_val(right_options,                                "01110000")
        self.rcode = get_mask_val(right_options,                       "00001111")
        self.qdcount, self.ancount, self.nscount, self.arcount = struct.unpack("!HHHH", data[4:4 + 8])
        data = data[12:]
        qname = b""
        while True:
            part_len = data[0]
            if not part_len:
                break
            qname += data[1:1 + part_len] + b"."
            data = data[1 + part_len:]
        data = data[1:]
        self.qname = qname
        self.qtype = QNAME_CODES[struct.unpack("!H", data[:2])[0]]
        self.qclass = QCLASS_CODES[struct.unpack("!H", data[2:4])[0]]
        data = data[4:]
        print(data)

    def __str__(self):
        attrs = filter(lambda x: "__" not in x, dir(self))
        return "\n".join("{} = {}".format(attr, getattr(self, attr))
                         for attr in attrs if not getattr(getattr(self, attr), "__call__", False))


def process_udp_client(server_socket, data, address):
    try:
        server_socket.sendto(data, address)
        packet = DNSPacket()
        packet.from_bytes(data, "UDP")
        print(packet)
    except Exception:
        print(traceback.format_exc())


def start_dns_server_with_udp():
    with ThreadPoolExecutor(MAX_WORKERS) as client_handler:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_server_socket:
            udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_server_socket.bind(("", PORT))
            while True:
                data, address = udp_server_socket.recvfrom(BUFFER_SIZE)
                print("Connection from: {}".format(address))
                client_handler.submit(process_udp_client, udp_server_socket, data, address)


def process_tcp_client(client_connection):
    try:
        data = client_connection.recv(BUFFER_SIZE)
        client_connection.send(data)
        packet = DNSPacket()
        packet.from_bytes(data, "TCP")
        print(packet)
        client_connection.close()
    except Exception:
        print(traceback.format_exc())


def start_dns_server_with_tcp():
    with ThreadPoolExecutor(MAX_WORKERS) as client_handler:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_server_socket:
            tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_server_socket.bind(("", PORT))
            tcp_server_socket.listen(MAX_WORKERS)
            while True:
                tcp_connection, address = tcp_server_socket.accept()
                print("Connection from: {}".format(address))
                client_handler.submit(process_tcp_client, tcp_connection)


def wait_clients():
    while True:
        time.sleep(1)
        print("Waiting. time: {}".format(time.time()))


def main():
    with ThreadPoolExecutor(MAX_WORKERS) as server_handler:
        server_handler.submit(start_dns_server_with_tcp)
        server_handler.submit(start_dns_server_with_udp)
        # server_handler.submit(wait_clients)


if __name__ == "__main__":
    main()
