from message import Message
from header import Header
from threading import Thread, Timer, RLock
from queue import Queue

from flags import Flag, Flags

class Connection(Thread):

    def __init__(self, addr, handler, streamID, window, timeout):
        super().__init__()
        self.addr = addr
        self.handler = handler
        self.buffer = Queue()
        self.done = False
        self.streamID = streamID
        self.lock = RLock()

        self.received = bytes()

        self.window = window
        self.inFlight = {}
        self.timers = {}

        self.timeout = timeout

        self.toSend = None

        self._sNum = 0
        self._aNum = 0
        self.duplicateAcks = 0
        self.lastReceivedAck = 0
        self.close = False



    def run(self):
        while not self.done:
            message = self.buffer.get()            
            self.state = self.state.changeState(self, message)
            print(self.state)
            
        self.handler.close_connection(self.streamID)


    def receive(self, message:Message):
        print("verifying message...")
        if message.verify():
            print("verified")
            self.ackPackages(message.header.aNum)

            print("Payload",message.payload[:message.header.dataLength])

            #self.aNum = message.header.sNum + message.header.dataLength
            #print("past akk")

            self.buffer.put(message)
        else:
            print("rejected")


    def send(self, message, pureAck = False):
        self.handler.send(message, self.addr)
        with self.lock:
            if not pureAck:
                self.inFlight[self.sNum] = message
                self.startTimer(self.sNum)
            

    def startTimer(self, sNum):
        timer = Timer(self.timeout, self.timerResend, [sNum])
        self.stopTimer(sNum)
        self.timers[sNum] = timer
        timer.start()
        #print("started timer", timer)


    def stopTimer(self, sNum):
        with self.lock:
            timer = self.timers.pop(sNum, None)
            print("stop timer", timer)
            if timer is not None:
                timer.cancel()  


    def ackPackages(self, aNum):
        with self.lock:
            received = [k for k in self.inFlight.keys() if k <= aNum]
            print(self.timers)
            for k in received:
                self.stopTimer(k)
                del self.inFlight[k]
            print("inF:: " + str(self.inFlight))


    def timerResend(self, sNum):
        #print("timersNow:", self.timers)
        with self.lock:
            self.send(self.inFlight[sNum])

    def resendInFlight(self):
        for sNum, m in self.inFlight.items():
            self.stopTimer(sNum)
            self.send(m)

    def sendData(self, ackIfNone = False):
        print("sending!!")
        if self.toSend is not None and not self.toSend.empty():
            print(self.window - len(self.inFlight))
            for _ in range(self.window - len(self.inFlight)):
                if self.toSend.empty():
                    print("done")
                    h = Header(self.streamID, self.sNum, self.aNum, Flags([Flag.F]), self.window)
                    m = Message(h)
                    self.send(m)
                    self.sNum +=1
                    return True
                payload = self.toSend.next(100)
                h = Header(self.streamID, self.sNum, self.aNum, Flags([Flag.A]), self.window)
                self.sNum += len(payload)
                m = Message(h, payload)
                m.to_bytes()
                print(m.verify())
                self.send(m)
        elif ackIfNone:
            h = Header(self.streamID, self.sNum, self.aNum, Flags([Flag.A]), self.window)
            self.send(Message(h), True)
        return False

    def wrtData(self, suffix):
        with open("rec" + suffix+".jpg", 'wb') as f:
            f.write(self.received)

    @property
    def sNum(self):
        return self._sNum % 65536
    @sNum.setter
    def sNum(self, num):
        self._sNum = num%65536

    @property
    def aNum(self):
        return self._aNum % 65536

    @aNum.setter
    def aNum(self, num):
        self._aNum = num % 65536
import state
    

    