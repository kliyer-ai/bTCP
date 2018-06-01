from header import Header
from flags import Flag
class TCPstatemachine:

    def __init__(self,streamID):
        self.streamID = streamID


class State:
    @staticmethod
    def changeState(statemachine,header):
        pass

class Established(State):
    @staticmethod
    def changeSate(statemachine,header):
        if header.flagSet(Flag.F):
            statemachine.sendAck()
            return Close_Wait

class Syn_Sent(State):
    @staticmethod
    def changeSate(statemachine, header):
        if header.flagSet(Flag.S) and header.flagSet(Flag.A):
            if statemachine.sendAck():
                statemachine.establish()
                return Established


class Syn_Rcvd(State):
    @staticmethod
    def changeSate(statemachine, header):
        if header.flagSet(Flag.A):
            statemachine.establish()
            return Established


class Last_Ack(State):
    @staticmethod
    def changeSate(statemachine, header):
        if header.flagSet(Flag.A):
            statemachine.close()
            return Closed

class Close_Wait(State):
    @staticmethod
    def changeSate(statemachine, header):
        if statemachine.sendFin():
            return Last_Ack


class Closed(State):
    @staticmethod
    def changeSate(statemachine, header):
        if header == 's':
            if statemachine.sendSyn():
                return Syn_Sent
        if header == 'c':
            if statemachine.sendSyn():
                statemachine.listen()
                return Listen
        return  Closed

class Listen(State):
    @staticmethod
    def changeState(statemachine,header):
        if header.flagSet(Flag.S):
            statemachine.sendSynAck()
            return Syn_Rcvd

#client

class Fin_Wait_1(State):
    @staticmethod
    def changeSate(statemachine, header):
        if header.flagSet(Flag.A):
            return Fin_Wait_2

class Fin_Wait_2(State):
    @staticmethod
    def changeSate(statemachine, header):
        if header.flagSet(Flag.F):
            statemachine.sendAck()
            return Time_Wait

class Time_Wait(State):
    @staticmethod
    def changeSate(statemachine, header):
        statemachine.close()
        return Closed