from struct import pack

class Header:

    def __init__(self, sPort, dPort, sNum, aNum, flags, window, uPointer = 0, options = 0):
        self.sPort = sPort
        self.dPort = dPort
        self.sNum = sNum
        self.aNum = aNum
        self.flags = flags
        self.window = window
        self.uPointer = uPointer
        self.options = options
        
    def to_bytes(self):
        header_format = ">HHIIBBHHH"
        bTCP_header = pack(header_format, self.sPort, self.dPort, self.sNum, self.aNum, self.flags.to_byte(), self.window, self.window)
        bTCP_header += bytes(self.options, 'asci')