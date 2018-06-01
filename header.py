from struct import pack, unpack
from flags import Flags

class Header:

    header_format = ">IHHBBHI"

    def __init__(self, streamID, sNum, aNum, flags, window, dataLength = 0, checksum = 0):
        self.streamID = streamID
        self.sNum = sNum
        self.aNum = aNum
        self.flags = flags
        self.window = window
        self.dataLength = dataLength
        self.checksum = checksum
        
    def to_bytes(self):
        bTCP_header = pack(Header.header_format, self.streamID, self.sNum, self.aNum, self.flags.to_byte(), self.window, self.dataLength, self.checksum)
        return bTCP_header

    @classmethod
    def from_bytes(cls,data):
        header = unpack(Header.header_format, data)
        return cls(header[0], header[1], header[2], Flags.from_byte(header[3]), header[4], header[5], header[6])

    def flagSet(self, flag):
        return flag in self.flags