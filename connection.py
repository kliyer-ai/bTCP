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

        self.sNum = 0
        self.aNum = 0
        self.duplicateAcks = 0
        self.lastReceivedAck = 0



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
            print("past akk")

            self.buffer.put(message)
        else:
            print("rejected")


    def send(self, message):
        self.handler.send(message, self.addr)

        with self.lock:
            sNum = message.header.sNum
            self.inFlight[sNum] = message
            self.startTimer(sNum)
            

    def startTimer(self, sNum):
        timer = Timer(self.timeout, self.timerResend, [sNum])
        self.stopTimer(sNum)
        self.timers[sNum] = timer
        timer.start()
        print("started timer", timer)


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
        print("timersNow:", self.timers)
        with self.lock:
            self.send(self.inFlight[sNum])

    def resendInFlight(self):
        for sNum, m in self.inFlight.items():
            self.stopTimer(sNum)
            self.send(m)

    def sendData(self):
         if self.toSend is not None and not self.toSend.empty():
                print(self.window - len(self.inFlight))
                for _ in range(self.window - len(self.inFlight)):
                    if self.toSend.empty():
                        print("done")
                        break

                    payload = self.toSend.next(10)                    
                    h = Header(self.streamID, self.sNum, self.aNum, Flags([Flag.A]), self.window)

                    self.sNum += len(payload)
                    m = Message(h, payload)
                    m.to_bytes()
                    print(m.verify())
                    self.send(m)
        else:
                h = Header(c.streamID, c.sNum, c.aNum, Flags([Flag.A]), c.window)
                c.send(Message(h))
                
import state
    

    