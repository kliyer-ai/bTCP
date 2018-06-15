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
                #if it fits
                if header.dataLength == 0:
                    if (c.lastReceivedAck == header.aNum):
                        c.duplicateAck += 1
                    else:
                        c.lastReceivedAck = header.aNum
                        c.duplicateAck = 0

                    if c.duplicateAck > 2:
                        c.resendInFlight()
                        return Established
                    elif c.duplicateAck == 0:
                        c.sendData()
                else:
                    #add data
                    c.received += message.payload[:header.dataLength]
                    c.aNum = message.header.sNum + message.header.dataLength  # update num
                    c.sendData(True)
            else:
                #duplicate Ack back - package did not fit
                h = Header(c.streamID, c.sNum, c.aNum, Flags([Flag.A]), c.window)
                c.send(Message(h))
            return Established

        if header.flagSet(Flag.F):
            return Close_Wait

class Syn_Sent(State):
    @staticmethod
    def changeState(c,  message):
        header = message.header
        if  header.flagSet(Flag.S) and  header.flagSet(Flag.A):
            c.aNum = header.aNum
            c.sNum += 1

            h = Header(c.streamID, c.sNum, c.aNum, Flags([Flag.A]), c.window)
            c.send(Message(h))
            c.sendData()
            return Established


class Syn_Rcvd(State):
    @staticmethod
    def changeState(c,  message):
        if  message.header.flagSet(Flag.A):
            return Established


class Last_Ack(State):
    @staticmethod
    def changeState(connection,  message):
        if  message.flagSet(Flag.A):
            connection.close()
            return Closed

class Close_Wait(State):
    @staticmethod
    def changeState(connection,  message):
        if connection.sendFin():
            return Last_Ack


class Closed(State):
    @staticmethod
    def changeState(connection,  message):
        if  message == 's':
            if connection.sendSyn():
                return Syn_Sent
        if  message == 'c':
            if connection.sendSyn():
                connection.listen()
                return Listen
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
            return Syn_Rcvd

#client

class Fin_Wait_1(State):
    @staticmethod
    def changeState(connection,  message):
        if  message.flagSet(Flag.A):
            return Fin_Wait_2

class Fin_Wait_2(State):
    @staticmethod
    def changeState(connection,  message):
        if  message.flagSet(Flag.F):
            connection.sendAck()
            return Time_Wait

class Time_Wait(State):
    @staticmethod
    def changeState(connection,  message):
        connection.close()
        return Closed