from connection import Connection
import state
from header import Header
from message import Message
from flags import Flags, Flag
from fileReader import FileReader

class ClientConnection(Connection):

    def __init__(self, addr,  handler, streamID, window, timeout, fileName):
        super().__init__(addr, handler, streamID, window, timeout)

        fr = FileReader()
        fr.read(fileName)
        self.toSend = fr

        self.state = state.Syn_Sent
        h = Header(self.streamID, self.sNum, self.aNum, Flags([Flag.S]), self.window)
        self.send(Message(h))