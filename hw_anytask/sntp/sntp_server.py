import datetime
import socket
import struct
import argparse
from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 256
NTP_PORT = 123
BUFFER_SIZE = 4096
TIME1900 = datetime.datetime(1900, 1, 1, 0, 0, 0)
SNTP_PACKET_FORMAT = "!BBBb20xQI4xI4x"


def get_false_time(delay):
    full_time = datetime.datetime.utcnow() - TIME1900
    return int(full_time.total_seconds()) + delay


def parse_client_data(client_data):
    vn = bin(client_data[0])[2:][2:5]
    poll = client_data[2]
    origin = struct.unpack("!Q", client_data[40:48])[0]
    return {'vn': vn, 'poll': poll, 'origin': origin}


def create_packet(receive_time, client_parameters, delay):
    header = int('00{}100'.format(client_parameters['vn']), 2)
    stratum = 3
    poll = client_parameters['poll']
    precision = 1
    origin_time = client_parameters['origin']
    sntp_packet = struct.pack(SNTP_PACKET_FORMAT, header, stratum, poll,
                              precision, origin_time,
                              receive_time, get_false_time(delay))
    return sntp_packet


def process_cleint(ntp_socket, client_data, client_address, delay):
    print("Processing client: {}".format(client_address))
    recieve_time = get_false_time(delay)
    client_parameters = parse_client_data(client_data)
    packet = create_packet(recieve_time, client_parameters, delay)
    ntp_socket.sendto(packet, client_address)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-d", "--delay", type=int, dest="delay", help="Delay for the client", default=0)
    argparser.add_argument("-p", "--port", type=int, dest="port", help="Server port", default=NTP_PORT)
    args = argparser.parse_args()
    delay = vars(args)["delay"]
    port = vars(args)["port"]
    print("Start sntp server at {} port with delay: {}".format(port, delay))
    ntp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ntp_socket.bind(("", NTP_PORT))
    with ntp_socket:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as client_handler:
            while True:
                client_data, client_address = ntp_socket.recvfrom(BUFFER_SIZE)
                client_handler.submit(process_cleint, ntp_socket, client_data, client_address, delay)


if __name__ == '__main__':
    main()
