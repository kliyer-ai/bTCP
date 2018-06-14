from queue import Queue
from message import Message
from connection import Connection
from threading import Lock
import select


class ConnectionHandler():

    def __init__(self, sock, window, timeout):
        self.connections = {}
        self.toSend = Queue()
        self.sock = sock
        self.lock = Lock()
        self.done = False

        self.window = window
        self.timeout = timeout
    
    def serve(self):
        while not self.done:
            r, _, _ = select.select([self.sock], [], [], 0.1) #timeout in s
            if r:
                s = r[0]
                data, addr = s.recvfrom(1016)
                message = Message.from_bytes(data)
                streamID = message.header.streamID
                print("recv message", message, streamID)

                if streamID in self.connections:
                    self.connections[streamID].receive(message)
                else:
                    c = Connection(addr, "s", self, streamID, self.window, self.timeout)
                    c.receive(message)
                    self.connections[streamID] = c
                    c.start()
                
            else:
                while not self.toSend.empty():
                    bMessage, addr = self.toSend.get()
                    self.sock.sendto(bMessage, addr) # this has to be a tuple


    def close_connection(self, streamID):
        with self.lock:
            del self.connections[streamID]

    def stop(self):
        self.done = True
        self.sock.close()

    def send(self, message, addr):
        print("send", addr, message)
        self.toSend.put((message.to_bytes(), addr))

    def addConnection(self, c):
        with self.lock:
            self.connections[c.streamID] = c
            c.start()
