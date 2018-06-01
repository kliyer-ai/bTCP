import socket
import abc
import random
import select

#socket wrapper - simulate different network
class SocketWrapper:
    
    def __init__(self, address):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(address)

        
    @abc.abstractmethod
    def sendto(self,data,addr):
        """
        Sends the package
        :param data:bytes object to be send
        :return: none
        """
        pass
    @abc.abstractmethod
    def recv(self):
        """
        blocks till package received
        :return: bytes
        """
        pass
    def close(self):
        self.s.close()


class Interferer:
    @abc.abstractmethod
    def apply(self, package):
        """
        applies interference
        :param package:
        :return:Message new Message
        """
class Dropper(Interferer):
    def __init__(self, lossrate=0.5):
        self.lossrate = lossrate
    def apply(self, package):
        if random.random() < self.lossrate:
            package = None
            print('package lost')
        return package

class Spurifier(Interferer):
    def __init__(self, bitNumber = 2, probability=0.5):
        self.probability = probability
        self.bitNumber = bitNumber

    def apply(self, package:bytes):
        if random.random() < self.probability:
            bar = bytearray(package)
            for i in range(self.bitNumber):
                r = random.randrange(len(bar))
                rb = random.randrange(255)
                bar[r] = rb
            package = bytes(bar)
            print('package spurified')
        return package


class perfectSocket(SocketWrapper):
    def __init__(self, address):
        super(perfectSocket, self).__init__(address)
        print(self.s)

    def sendto(self,data, addr):
        self.s.sendto(data,addr)

    def recv(self):
        r, _, _ = select.select([self.s], [], [], 0.1) #timeout in s
        if r:
            s = r[0]
            return s.recvfrom(1016)
        else:
            return None


class lossySocket(perfectSocket):
    def __init__(self, address, interferers:Interferer):
        super(lossySocket, self).__init__(address)
        print(self.s, "interfs:", interferers)
        self.interferers:[Interferer] = interferers

    def sendto(self, data,addr):
        for i in self.interferers :
            data = i.apply(data)
        if data != None:
            self.s.sendto(data, addr)

if __name__ == "__main__":
    #p=perfectSocket(('localhost', 4334))
    l = lossySocket(('localhost', 4334),[Dropper(0.3), Spurifier(2,0.2)])
    for i in range(10):
        l.sendto(bytes(12),('localhost',3434))
    #p.close()
    l.close()