from message import Message
from header import Header
from threading import Thread, Timer, Lock
from queue import Queue
import state
from flags import Flag, Flags

class Connection(Thread):

    def __init__(self, addr, handler, streamID, window, timeout):
        super().__init__()
        self.addr = addr
        self.handler = handler
        self.buffer = Queue()
        self.done = False
        self.streamID = streamID
        self.lock = Lock()

        self.window = window
        self.inFlight = {}
        self.timers = {}

        self.timeout = timeout

        self.sNum = 0
        self.aNum = 0
        self.duplicateAcks = 0
        self.lastAck = 0



    def run(self):
        while not self.done:
            message = self.buffer.get()            
            self.state = self.state.changeState(self, message)
            print(self.state)
            
        self.handler.close_connection(self.streamID)


    def receive(self, message:Message):
        if message.verify():
            self.ackPackages(message.header.aNum)

            #self.aNum = message.header.sNum + message.header.dataLength


            self.buffer.put(message)


    def send(self, message):
        self.handler.send(message, self.addr)

        with self.lock:
            sNum = message.header.sNum
            timer = Timer(self.timeout, self.resend, [sNum])
            self.timers[sNum] = timer
            self.inFlight[sNum] = message

            timer.start()


    def stopTimers(self, toStop):
        with self.lock:
            for k in toStop:
                timer = self.timers.pop(k)
                timer.cancel()


    def ackPackages(self, threshold):
        with self.lock:
            received = [k for k in self.inFlight.keys() if k <= threshold]
            self.stopTimers(received)
            for k in received:
                del self.inFlight[k]


    def resend(self, sNum):
        with self.lock:
            self.send(self.inFlight.pop(sNum))

    

    