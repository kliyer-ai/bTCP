#!/usr/local/bin/python3
import socket, argparse
from message import Message
from connection import Connection
from queue import Queue
import socketWrapper
from connection_handler import ConnectionHandler

#Handle arguments
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
parser.add_argument("-o","--output", help="Where to store file", default="tmp.file")
args = parser.parse_args()

server_ip = "127.0.0.1"
server_port = 9001


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #socketWrapper.perfectSocket(("localhost",9001)) # UDP
sock.bind((server_ip, server_port))

ch = ConnectionHandler(sock, args.window, args.timeout)

try:
    ch.serve()
except KeyboardInterrupt:
    ch.stop()