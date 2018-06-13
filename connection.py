from message import Message
from threading import Thread
from queue import Queue
import state

class Connection(Thread):

    def __init__(self, addr, mode, handler, streamID):
        super().__init__()
        self.addr = addr
        self.handler = handler
        self.timer = {}
        self.buffer = Queue()
        self.done = False
        self.timeouts = {}
        self.streamID = streamID

        self.data = bytes()
        self.seq = 0
        self.ack = 0

        if mode == "s":
            self.state = state.Listen
        else:
            self.state = state.Syn_Sent

        


    def run(self):
        while not self.done:
            message = self.buffer.get()
            self.state = self.state.changeState(self, message)
            
        self.handler.close_connection(self.streamID)


    def receive(self, message:Message):
        if message.verify():
            self.buffer.put(message)




    