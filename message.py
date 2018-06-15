import binascii
from header import Header
import copy

class Message():

    def __init__(self, header, payload:bytes = bytes()):
        self.header = header
        self.payload = payload

    def to_bytes(self):
        # set message length
        dataLength = len(self.payload)
        self.header.dataLength = dataLength

        # pad payload
        padded_payload = bytearray(1000)
        padded_payload[0:dataLength] = self.payload
        padded_payload = bytes(padded_payload)
        
        self.header.checksum = 0
        # concetinate header and payload
        binary_message = self.header.to_bytes() + padded_payload

        # calculate checksum
        checksum = binascii.crc32(binary_message)

        # combine everything
        self.header.checksum = checksum

        return self.header.to_bytes() + padded_payload

    @classmethod
    def from_bytes(cls, data):
        headerData = data[:16]
        payload = data[16:]
        header = Header.from_bytes(headerData)
        return cls(header, payload)


    def verify(self):
        header = copy.deepcopy(self.header) 
        checksum = header.checksum
        header.checksum = 0
        bHeader = header.to_bytes()
        return checksum == binascii.crc32(bHeader + self.payload)

    def __str__(self):
        return "Message" + 


