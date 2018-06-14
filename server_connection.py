from connection import Connection
import state

class ServerConnection(Connection):

    def __init__(self, addr,  handler, streamID, window, timeout):
        super().__init__(addr, handler, streamID, window, timeout)

        self.received = bytes()

        self.state = state.Listen