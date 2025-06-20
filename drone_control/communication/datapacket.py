
from .serialization import Packet

class AckPacket(Packet):

    PTYPE = 1
    
    STATUS_OK = 0

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

    CONNECT = 1
    DISCONNECT = 0

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

    def __init__(self, pid, ptype=PTYPE) -> None:
        super().__init__(pid, ptype)

    def __iter__(self):
        return iter([self.pid, self.ptype])
    

class EndCapturePacket(Packet):

    PTYPE = 4

    def __init__(self, pid, ptype=PTYPE):
        super().__init__(pid, ptype)
    
    def __iter__(self):
        return iter([self.pid, self.ptype])

class CloseServerPacket(Packet):

    PTYPE = 5

    def __init__(self, pid, ptype=PTYPE):
        super().__init__(pid, ptype)
    
    def __iter__(self):
        return iter([self.pid, self.ptype])

class PosePacket(Packet):

    PTYPE = 6

    def __init__(self, pid, timestamp, x, y, z, yaw, ptype=PTYPE):
        super().__init__(pid, ptype)
        self.__timestamp = timestamp
        self.__x = x
        self.__y = y
        self.__z = z
        self.__yaw = yaw
    
    def __iter__(self):
        return iter([self.pid, self.ptype, self.__timestamp, self.__x, self.__y, self.__z, self.__yaw])
    
    def __get_timestamp(self):
        return self.__timestamp
    
    def __get_x(self):
        return self.__x
    
    def __get_y(self):
        return self.__y
    
    def __get_z(self):
        return self.__z
    
    def __get_yaw(self):
        return self.__yaw

    timestamp = property(__get_timestamp)
    x = property(__get_x)
    y = property(__get_y)
    z = property(__get_z)
    yaw = property(__get_yaw)

class StartTimedCapturePacket(Packet):

    PTYPE = 7
    
    def __init__(self, pid, ptype=PTYPE, captureTime=1.0) -> None:
        super().__init__(pid, ptype)
        self.__captureTime = captureTime
        
    def __get_captureTime(self):
        return self.__captureTime
    
    captureTime = property(fget=__get_captureTime)

    def __iter__(self):
        return iter([self.pid, self.ptype, self.captureTime])

class EndTimedCapturePacket(Packet):
    
    PTYPE = 8
    
    def __init__(self, pid, ptype=PTYPE) -> None:
        super().__init__(pid, ptype)

    def __iter__(self):
        return iter([self.pid, self.ptype])
