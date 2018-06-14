from message import Message
from header import Header
from threading import Thread, Timer
from queue import Queue
import state
from flags import Flag, Flags

class Connection(Thread):

    def __init__(self, addr, mode, handler, streamID, window, timeout):
        super().__init__()
        self.addr = addr
        self.handler = handler
        self.timers = {}
        self.buffer = Queue()
        self.done = False
        self.streamID = streamID

        self.window = window
        self.inFlight = 0

        self.timeout = timeout


        self.received = bytes()
        self.toSend = None

        self.sNum = 0
        self.aNum = 0
        self.duplicateAcks = 0

        if mode == "s":
            self.state = state.Listen
        elif mode == "c":
            self.state = state.Syn_Sent
            h = Header(self.streamID, self.sNum, self.aNum, Flags([Flag.S]), self.window)
            self.send(Message(h))
            
        print(self.state)
        


    def run(self):
        while not self.done:
            message = self.buffer.get()
            
            self.state = self.state.changeState(self, message)
            print(self.state)
            
        self.handler.close_connection(self.streamID)


    def receive(self, message:Message):
        if message.verify():
            print("verified")
            self.stopTimer(message.header.aNum)
            self.buffer.put(message)

    def send(self, message):
        self.handler.send(message, self.addr)
        timer = Timer(1, self.send, [message])
        self.timers[message.header.sNum] = timer
        timer.start()

    def stopTimer(self, threshold):
        toStop = [k for k in self.timers.keys() if k <= threshold]
        for k in toStop:
            timer = self.timers.pop(k)
            timer.cancel()



    