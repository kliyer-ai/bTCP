from enum import IntEnum
from struct import pack

class Flags():

    def __init__(self, flags):
        self.flags = flags

    def to_byte(self):
        out = b'\x00'[0]
        for f in self.flags:
            out = out | f.value
        return out

    @classmethod
    def from_byte(cls, byte):
        flags = []
        for f in Flag:
            if byte & f.value:
                flags.append(f)
        return cls(flags)


class Flag(IntEnum):
    C = 128 
    E = 64
    U = 32
    A = 16
    P = 8
    R = 4
    S = 2
    F = 1

