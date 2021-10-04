
from .serialization import Packet

class AckPacket(Packet):

    def __init__(self, pid, ackPid, status, ptype=1) -> None:
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

class TracePacket(Packet):
    def __init__(self, pid, yaw, pitch, roll, ptype=2) -> None:
        super().__init__(pid, ptype)
        self.__yaw = yaw
        self.__pitch = pitch
        self.__roll = roll
    
    def __iter__(self):
        return iter([self.pid, self.ptype, self.__yaw, self.__pitch, self.__roll])
    
    def __getYaw(self):
        return self.__yaw
    
    def __getPitch(self):
        return self.__pitch
    
    def __getRoll(self):
        return self.__roll
    
    yaw = property(__getYaw)
    pitch = property(__getPitch)
    roll = property(__getRoll)
    
