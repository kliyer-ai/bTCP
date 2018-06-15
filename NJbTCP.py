from client_connection import ClientConnection
from server_connection import  ServerConnection
from connection_handler import ConnectionHandler
import random
import socket
import argparse

def startServer(ip, port):
    fileName = input("Enter filename for the new file: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))

    ch = ConnectionHandler(sock, 100, 1, fileName)
    ch.serve()

def startClient(ip, port):
    fileName = input("Enter filename: ")

    # launch localhost client connecting to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", random.randint(10000, 60000)))

    ch = ConnectionHandler(sock, 100, 0.1)

    # create connection
    streamID = random.randint(0, 2 ^ 32 - 1)
    c = ClientConnection((ip, port), ch, streamID, 100,
                         1, fileName)

    # client sends content to server
    ch.addConnection(c)
    ch.serve()
    print("File sent biatch!")



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", help="choose the mode", default="c")
    parser.add_argument("-i", "--ip", help="ip address", default="0.0.0.0")
    parser.add_argument("-p", "--port", help="port", type=int, default=11000)
    args = parser.parse_args()

    if(args.mode == "s"):
        startServer(args.ip, args.port)
    elif(args.mode == "c"):
        startClient(args.ip, args.port)
    else:
        print("unsupported mode")


