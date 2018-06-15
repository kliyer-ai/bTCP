from header import Header
from message import Message
from flags import Flag, Flags
from connection import Connection

class State:
    @staticmethod
    def changeState(connection, message):
        print("ERROR")
        pass

class Established(State):
    @staticmethod
    def changeState(c: Connection, message: Message):
        header = message.header

        if  header.flagSet(Flag.A):
            if header.sNum == c.aNum:
                c.ackPackages(header.aNum)
                
                #if it fits
                if header.dataLength == 0:
                    if (c.lastReceivedAck == header.aNum):
                        c.duplicateAcks += 1
                    else:
                        c.lastReceivedAck = header.aNum
                        c.duplicateAcks = 0
                        if c.sendData():
                            return Fin_Wait_1


                    if c.duplicateAcks > 2:
                        c.resendInFlight()
                        if c.sendData():
                            return Fin_Wait_1
                else:
                    #add data
                    c.lastReceivedAck = header.aNum
                    c.received += message.payload[:header.dataLength]
                    c.aNum = message.header.sNum + message.header.dataLength  # update num
                    if c.sendData(True):
                        return Fin_Wait_1
            else:
                #duplicate Ack back - package did not fit
                h = Header(c.streamID, c.sNum, c.aNum, Flags([Flag.A]), c.window)
                c.send(Message(h), True)
            return Established

        if header.flagSet(Flag.F):
            h = Header(c.streamID, c.sNum, c.aNum, Flags([Flag.F]), c.window)
            message = Message(h)
            c.send(message)
            c.sNum +=1
            return Close_Wait
        return Established

class Syn_Sent(State):
    @staticmethod
    def changeState(c,  message):
        header = message.header
        if  header.flagSet(Flag.S) and  header.flagSet(Flag.A):
            c.aNum = header.aNum
            c.sNum += 1

            h = Header(c.streamID, c.sNum, c.aNum, Flags([Flag.A]), c.window)
            c.send(Message(h),True)
            c.ackPackages(header.aNum)
            if c.sendData():
                return Fin_Wait_1
            return Established
        return Syn_Sent


class Syn_Rcvd(State):
    @staticmethod
    def changeState(c,  message):
        if  message.header.flagSet(Flag.A):
            c.ackPackages(message.header.aNum)
            return Established
        return Syn_Rcvd


class Last_Ack(State):
    @staticmethod
    def changeState(connection,  message):
        if  message.flagSet(Flag.A):
            connection.close()
            return Closed

class Close_Wait(State):
    @staticmethod
    def changeState(c,  message):
        if  message.header.flagSet(Flag.A):
            c.close = True
            c.wrtData("Server")
            c.ackPackages(message.header.aNum + 1)

            return Closed
        return Close_Wait


class Closed(State):
    @staticmethod
    def changeState(connection,  message):
        return  Closed

class Listen(State):
    @staticmethod
    def changeState(c, message):
        header = message.header
        if  header.flagSet(Flag.S):
            c.window = header.window
            c.aNum += 1
            h = Header(c.streamID, c.sNum, c.aNum, Flags([Flag.A, Flag.S]), c.window)
            message = Message(h)
            c.send(message)
            c.sNum +=1
            return Syn_Rcvd
        return Listen

#client

class Fin_Wait_1(State):
    @staticmethod
    def changeState(c,  message):
        if  message.header.flagSet(Flag.F):
            c.aNum +=1
            c.ackPackages(message.header.aNum + 1)
            h = Header(c.streamID, c.sNum, c.aNum, Flags([Flag.A]), c.window)
            m = Message(h)
            c.send(m, True)
            c.resetFinTimer()
            return Time_Wait
        return Fin_Wait_1


class Time_Wait(State):

    @staticmethod
    def changeState(c,  message):
        header = message.header
        if header.flagSet(Flag.F):
            c.ackPackages(message.header.aNum + 1)
            h = Header(c.streamID, c.sNum, c.aNum, Flags([Flag.A]), c.window)
            m = Message(h)
            c.send(m, True)
            c.resetFinTimer()
            return Time_Wait
        return Closed