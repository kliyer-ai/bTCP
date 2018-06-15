from message import Message
from header import Header
from threading import Thread, Timer, RLock
from queue import Queue

from flags import Flag, Flags

class Connection(Thread):

    def __init__(self, addr, handler, streamID, window, timeout, outFileName=None):
        super().__init__()
        self.addr = addr
        self.handler = handler
        self.buffer = Queue()
        self.done = False
        self.streamID = streamID
        self.lock = RLock()
        self.allAcks = set()

        self.outFileName = outFileName


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
        self.deltS = set()
        self.closeTimer = None

    def run(self):
        while not self.done:
            message = self.buffer.get()

            if message is None:
                break

            self.allAcks.add(message.header.sNum)

            print("------------------------")
            print(sorted(self.allAcks))
            print("c ack", self.aNum)
            print("message", message)
            print("Payload",message.payload[:message.header.dataLength])

            self.state = self.state.changeState(self, message)
            print(self.state)
            print("------------------------------------")

        print("Connection is done")
        #self.handler.close_connection(self.streamID)


    def receive(self, message:Message):
        if message is None:
            self.buffer.put(None)
        elif message.verify():
            self.buffer.put(message)



    def send(self, message, pureAck = False):
        self.handler.send(message, self.addr)
        with self.lock:
            if not pureAck:
                self.inFlight[message.header.sNum] = message
                self.startTimer(message.header.sNum)


    def startTimer(self, sNum):
        with self.lock:
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
            received = [k for k in self.inFlight.keys() if k < aNum]
            print(self.timers)
            for k in received:
                self.stopTimer(k)
                del self.inFlight[k]
                self.deltS.add(k)
            print("inF:: " + str(self.inFlight))


    def timerResend(self, sNum):
        #print("timersNow:", self.timers)
        with self.lock:
            self.send(self.inFlight[sNum])

    def resendInFlight(self):
        with self.lock:
            for sNum, m in self.inFlight.items():
                self.stopTimer(sNum)
                self.send(m)

    def sendData(self, ackIfNone = False):
        print("sending!!")
        if self.toSend is not None:
            print(self.window - len(self.inFlight))
            for _ in range(self.window - len(self.inFlight)):
                if self.toSend.empty():
                    if len(self.inFlight) == 0:
                        print("done")
                        h = Header(self.streamID, self.sNum, self.aNum, Flags([Flag.F]), self.window)
                        m = Message(h)
                        self.send(m)
                        self.sNum += 1
                        return True
                    return False

                payload = self.toSend.next(100)
                h = Header(self.streamID, self.sNum, self.aNum, Flags([Flag.A]), self.window)
                m = Message(h, payload)
                self.send(m)
                self.sNum += len(payload)
        elif ackIfNone:
            h = Header(self.streamID, self.sNum, self.aNum, Flags([Flag.A]), self.window)
            self.send(Message(h), True)
        return False

    def wrtData(self, suffix):
        if self.outFileName is not None:
            with open(self.outFileName, 'wb') as f:
                f.write(self.received)
        else:
            with open("rec" + suffix + ".jpg", 'wb') as f:
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

    def stopClient(self):
        self.handler.stop()

    def stopConnection(self, streamID):
        self.handler.close_connection(streamID)

    def resetFinTimer(self):
        if self.closeTimer is not None:
            self.closeTimer.cancel()
        self.closeTimer = Timer(self.timeout * 10, self.writeAndclose)
        self.closeTimer.start()


    def writeAndclose(self):
        print("Dying")
        self.close = True
        self.wrtData("Client")
        self.stopClient()



    