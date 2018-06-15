#!/usr/local/bin/python3
import socket, argparse, random
from struct import pack
from random import randint
from connection_handler import ConnectionHandler
from fileReader import FileReader
from client_connection import ClientConnection

#Handle arguments
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=8)
parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=5)
parser.add_argument("-i","--input", help="File to send", default="tmp.file")
args = parser.parse_args()

server_ip = "127.0.0.1"
server_port = 9002


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #socketWrapper.perfectSocket(("localhost",9001)) # UDP
sock.bind((server_ip, server_port))

ch = ConnectionHandler(sock, args.window, args.timeout)

# get file to send
fileName = "text.txt"# input("Enter file name: ")

# create connection
streamID = 1111
c = ClientConnection(("127.0.0.1", 9001), ch, streamID, args.window, args.timeout, fileName)

# add connection 
ch.addConnection(c)





try:
    ch.serve()
    
except KeyboardInterrupt:
    ch.stop()

