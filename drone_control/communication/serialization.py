import abc

class Packet(abc.ABC):

    def __init__(self, pid, ptype):
        self.__pid = pid
        self.__ptype = ptype

    def __get_pid(self):
        return self.__pid

    def __get_ptype(self):
        return self.__ptype

    pid = property(__get_pid)
    ptype = property(__get_ptype)


class Serialization:
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    @abc.abstractmethod
    def pack(cls, packet: Packet) -> list:
        """
        Apply a serialization method to pack
        """
        raise NotImplementedError("Pack not implemented. Use subclasses")

    @staticmethod
    @abc.abstractmethod
    def unpack(cls, list_packet: list) -> Packet:
        """
        Apply a deserialization method to unpack
        """
        raise NotImplementedError("Unpack not implemented. Use subclasses")

class Serializator:
    """
    Choose an Serialization method to pack-unpack a received packet
    """

    @staticmethod
    @abc.abstractmethod
    def pack(cls, packet: Packet) -> bytes:
        """
        Convert Packet to byte
        """
        raise NotImplementedError("Pack not implemented. Use subclasses")

    @staticmethod
    @abc.abstractmethod
    def unpack(cls, byte_packet: bytes) -> Packet:
        """
        Convert a bytes to Packet, selecting a serialization method
        """
        raise NotImplementedError("Unpack not implemented. Use subclasses")