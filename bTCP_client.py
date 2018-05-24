#!/usr/local/bin/python3
import socket, argparse, random
from struct import pack
from random import randint

#Handle arguments
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
parser.add_argument("-i","--input", help="File to send", default="tmp.file")
args = parser.parse_args()

destination_ip = "127.0.0.1"
destination_port = 9001

#bTCP header


bTCP_payload = ""
udp_payload = bTCP_header

#UDP socket which will transport your bTCP packets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#send payload
sock.sendto(udp_payload, (destination_ip, destination_port))
