#!/usr/bin/python3

import traceback
from concurrent.futures import ThreadPoolExecutor
import socket
import struct
import binascii
from zone_file_parser import parse_zone_file, get_record
import argparse
import os

BUFFER_SIZE = 64 * 1024
MAX_WORKERS = 256
QNAME_CODES = {1: "A", 2: "NS", 5: "CNAME", 12: "PTR", 13: "HINFO", 15: "MX", 252: "AXFR", 255: "ANY",
               "A": 1, "NS": 2, "CNAME": 5, "PTR": 12, "HINFO": 13, "MX": 15, "AXFR": 252, "ANY": 255}
QCLASS_CODES = {1: "IN",
                "IN": 1}
LENS = {"A": 4, "AAAA": 16}
ZONE_LIST = list(parse_zone_file(open("usaaa.ru.dns")))


def get_mask_val(data, mask: str) -> int:
    if len(mask) != 8:
        raise Exception
    return data & int(mask, 2)


def nice_hex(data):
    d = binascii.hexlify(data).decode()
    return " ".join(d[i * 2:i * 2 + 2] for i in range(len(d) // 2))


class DNSPacket:
    def __init__(self, data, transport_protocol):
        self.data = data
        # print(nice_hex(data))
        if transport_protocol.lower() == "tcp":
            self.message_len = struct.unpack("!H", data[:2])
            data = data[2:]
        elif transport_protocol.lower() != "udp":
            raise ValueError("Unexpected protocol type: {}".format(transport_protocol))
        self.id = struct.unpack("!H", data[:2])
        left_options = data[2]
        right_options = data[3]
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
        self.pointers = []
        self.pointer = 12
        self.questions = []
        self.answers = []
        self.authority_records = []  # not supported
        self.addition_section = []  # not supported
        for index in range(self.qdcount):
            self.pointers.append(self.pointer)
            qname = b""
            while True:
                part_len = data[0]
                if not part_len:
                    break
                qname += data[1:1 + part_len] + b"."
                data = data[1 + part_len:]
                self.pointer += 1 + part_len
            data = data[1:]
            self.pointer += 1
            qtype = QNAME_CODES[struct.unpack("!H", data[:2])[0]]
            qclass = QCLASS_CODES[struct.unpack("!H", data[2:4])[0]]
            self.questions.append((qname.decode(), qtype, qclass))
            data = data[4:]
        if data:
            self.data = self.data[:-len(data)]

    def __str__(self):
        attrs = filter(lambda x: "__" not in x, dir(self))
        return "\n".join("{} = {}".format(attr, getattr(self, attr))
                         for attr in attrs if not getattr(getattr(self, attr), "__call__", False))

    def create_answer(self, zone_file):
        for index in range(len(self.questions)):
            for record in get_record(self.questions[index][0], self.questions[index][1], parse_zone_file(zone_file)):
                qname = struct.pack("!H", self.pointers[index] | 49152)
                qtype = struct.pack("!H", QNAME_CODES[record[1]])
                qclass = struct.pack("!H", QCLASS_CODES[record[2]])
                ttl = struct.pack("!I", record[3] - 1)
                length = struct.pack("!H", 4)
                if record[1] == "A":
                    args = ("!BBBB",) + tuple(map(int, record[4].split(".")))
                    rdata = struct.pack(*args)
                else:
                    raise ValueError("Bad record type {} not supported".format(record[1]))
                self.answers.append(qname + qtype + qclass + ttl + length + rdata)
        data = bytearray(self.data)
        data[2] |= 128
        data[3] &= 127  # RCODE is here
        data[6:8] = struct.pack("!H", len(self.answers))
        for answer in self.answers:
            data.extend(answer)
        return bytes(data)


def process_udp_client(server_socket, data, address, zone_file):
    try:
        packet = DNSPacket(data, "UDP")
        answer = packet.create_answer(zone_file)
        server_socket.sendto(answer, address)
    except Exception:
        print(traceback.format_exc())


def start_dns_server_with_udp(port, zone_file):
    with ThreadPoolExecutor(MAX_WORKERS) as client_handler:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_server_socket:
            udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_server_socket.bind(("", port))
            while True:
                data, address = udp_server_socket.recvfrom(BUFFER_SIZE)
                print("Connection from: {}".format(address))
                client_handler.submit(process_udp_client, udp_server_socket, data, address, zone_file)


def process_tcp_client(client_connection, zone_file):
    try:
        data = client_connection.recv(BUFFER_SIZE)
        packet = DNSPacket(data, "TCP")
        client_connection.send(packet.create_answer(zone_file))
        client_connection.close()
    except Exception:
        print(traceback.format_exc())


def start_dns_server_with_tcp(port, zone_file):
    with ThreadPoolExecutor(MAX_WORKERS) as client_handler:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_server_socket:
            tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_server_socket.bind(("", port))
            tcp_server_socket.listen(MAX_WORKERS)
            while True:
                tcp_connection, address = tcp_server_socket.accept()
                print("Connection from: {}".format(address))
                client_handler.submit(process_tcp_client, tcp_connection, zone_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", dest="port", default=53, type=int, help="port for dns server")
    parser.add_argument("-f", "--file-zone", dest="file_zone", help="zone file for opening")
    parser.add_argument("fqdn", help="fully qualified domain name")
    args = parser.parse_args()
    port = args.port
    fqdn = args.fqdn
    filename_zone = "{}.dns".format(fqdn) if args.file_zone is None else args.file_zone
    if not os.path.isfile(filename_zone):
        print("File {} doesn't exist".format(filename_zone))
        return
    print("Start DNS server:\nFQDN = {}\nport = {}\nzone file = {}\n".format(fqdn, port, filename_zone))
    with open(filename_zone) as zone_file:
        zone_file_lines = zone_file.read().split("\n")
        with ThreadPoolExecutor(MAX_WORKERS) as server_handler:
            server_handler.submit(start_dns_server_with_tcp, port, zone_file_lines)
            server_handler.submit(start_dns_server_with_udp, port, zone_file_lines)


if __name__ == "__main__":
    main()
