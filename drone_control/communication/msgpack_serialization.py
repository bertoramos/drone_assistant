
import msgpack

from . import datapacket
from . import serialization as st

class AckPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.AckPacket, "Error : packet is not a AckPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 4, "Error: No valid ack packet"
        assert list_packet[1] == datapacket.AckPacket.PTYPE, "Error: list_packet is not a ack packet"
        return datapacket.AckPacket(list_packet[0], list_packet[2], list_packet[3])

class ModePacketMsgPackSerialization(st.Serialization):

    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.ModePacket, "Error : packet is not a ModePacket"
        l = list(iter(packet))

        return list(iter(packet))
    
    @staticmethod
    def unpack(list_packet):
        assert len(list_packet) == 3, "Error: No valid mode packet"
        assert list_packet[1] == datapacket.ModePacket.PTYPE, "Error: list_packet is not a mode packet"

        return datapacket.ModePacket(list_packet[0], list_packet[2])

class StartCapturePacketMsgPackSerialization(st.Serialization):

    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.StartCapturePacket, "Error: packet is not a StartCapturePacket"
        l = list(iter(packet))
        return list(iter(packet))
    
    @staticmethod
    def unpack(list_packet: list):
        assert len(list_packet) == 2, "Error: No valid start capture packet"
        assert list_packet[1] == datapacket.StartCapturePacket.PTYPE, "Error: list_packet is not a start capture packet"

        return datapacket.StartCapturePacket(list_packet[0])


class EndCapturePacketMsgPackSerialization(st.Serialization):

    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.EndCapturePacket, "Error: packet is not a EndCapturePacket"
        l = list(iter(packet))
        return list(iter(packet))
    
    @staticmethod
    def unpack(list_packet: list):
        assert len(list_packet) == 2, "Error: No valid end capture packet"
        assert list_packet[1] == datapacket.EndCapturePacket.PTYPE, "Error: list_packet is not a end capture packet"

        return datapacket.EndCapturePacket(list_packet[0])


class CloseServerPacketMsgPackSerialization(st.Serialization):

    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.CloseServerPacket, "Error: packet is not a CloseServerPacket"
        l = list(iter(packet))
        return list(iter(packet))
    
    @staticmethod
    def unpack(list_packet: list):
        assert len(list_packet) == 2, "Error: No valid close server packet"
        assert list_packet[1] == datapacket.CloseServerPacket.PTYPE, "Error: list_packet is not a close server packet"

        return datapacket.CloseServerPacket(list_packet[0])


class PosePacketMsgPackSerialization(st.Serialization):

    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.PosePacket, "Error: packet is not a PosePacket"
        return list(iter(packet))
    
    @staticmethod
    def unpack(list_packet: list):
        assert len(list_packet) == 7, "Error: No valid pose packet"
        assert list_packet[1] == datapacket.PosePacket.PTYPE, "Error: list_packet is not a pose packet"

        return datapacket.PosePacket(list_packet[0])


# { ptype : SerializationClass, ... }
# choose_serialization.get(ptype) -> return: ptype pack/unpack method
choose_serialization = {
                        datapacket.AckPacket.PTYPE: AckPacketMsgPackSerialization,
                        datapacket.ModePacket.PTYPE: ModePacketMsgPackSerialization,
                        datapacket.StartCapturePacket.PTYPE: StartCapturePacketMsgPackSerialization,
                        datapacket.EndCapturePacket.PTYPE: EndCapturePacketMsgPackSerialization,
                        datapacket.CloseServerPacket.PTYPE: CloseServerPacketMsgPackSerialization,
                        datapacket.PosePacket.PTYPE: PosePacketMsgPackSerialization
                        }

class MsgPackSerializator(st.Serializator):

    @staticmethod
    def pack(packet: st.Packet) -> bytes:
        ptype = packet.ptype
        cipher_method = choose_serialization.get(ptype)
        if cipher_method is None:
            raise "Error: Serialization method not found (pack). Check packet type identification"
        values = cipher_method.pack(packet)
        return msgpack.packb(values, use_bin_type=True)

    @staticmethod
    def unpack(byte_packet: bytes) -> st.Packet:
        values = msgpack.unpackb(byte_packet)
        ptype = values[1]
        decipher_method = choose_serialization.get(ptype)
        if decipher_method is None:
            raise "Error: Serialization method not found (unpack). Check packet type identification"
        return decipher_method.unpack(values)
