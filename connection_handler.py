from queue import Queue
from message import Message
from connection import Connection
from threading import Lock


class ConnectionHandler():

    def __init__(self, sock, mode):
        self.connections = {}
        self.toSend = Queue()
        self.sock = sock
        self.mode = mode
        self.lock = Lock()
        self.done = False
    
    def serve(self):
        while not self.done:
            response = self.sock.recv()
            if response:
                data, addr = response
                message = Message.from_bytes(data)
                streamID = message.header.streamID

                if streamID in self.connections:
                    self.connections[streamID].receive(message)
                else:
                    c = Connection(addr, "s", self, streamID)
                    self.connections[streamID] = c
                    c.start()
                
            else:
                while not self.toSend.empty():
                    self.sock.sendto(self.toSend.get()) # this has to be a tuple

    def close_connection(self, streamID):
        with self.lock:
            del self.connections[streamID]

    def stop(self):
        self.done = True
        self.sock.close()