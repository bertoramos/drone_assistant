
from .serialization import Packet

class AckPacket(Packet):

    PTYPE = 1

    def __init__(self, pid, ackPid, status, ptype=PTYPE) -> None:
        super().__init__(pid, ptype)
        self.__ackPid = ackPid
        self.__status = status
    
    def __iter__(self):
        return iter([self.pid, self.ptype, self.__ackPid, self.__status])
    
    def __getAckPid(self):
        return self.__ackPid
    
    def __getStatus(self):
        return self.__status

    ackPid = property(__getAckPid)
    status = property(__getStatus)

class ModePacket(Packet):

    PTYPE = 2

    def __init__(self, pid, mode, ptype=PTYPE) -> None:
        super().__init__(pid, ptype)
        self.__mode = mode
    
    def __iter__(self):
        return iter([self.pid, self.ptype, self.__mode])
    
    def __getMode(self):
        return self.__mode

    mode = property(__getMode)


class StartCapturePacket(Packet):

    PTYPE = 3

    def __init__(self, pid, captureTime, ptype=PTYPE) -> None:
        super().__init__(pid, ptype)
        self.__captureTime = captureTime
    
    def __iter__(self):
        return iter([self.pid, self.ptype, self.__captureTime])

    def __get_captureTime(self):
        return self.__captureTime
    
    captureTime = property(__get_captureTime)

class EndCapturePacket(Packet):

    PTYPE = 4

    def __init__(self, pid, ptype=PTYPE):
        super().__init__(pid, ptype)
    
    def __iter__(self):
        return iter([self.pid, self.ptype])

