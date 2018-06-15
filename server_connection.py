from connection import Connection
import state

class ServerConnection(Connection):

    def __init__(self, addr,  handler, streamID, window, timeout, fileName=None):
        super().__init__(addr, handler, streamID, window, timeout, fileName)

        self.state = state.Listen
