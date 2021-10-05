
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
        assert list_packet[1] == 1, "Error: list_packet is not a ack packet"
        return datapacket.AckPacket(list_packet[0], list_packet[2], list_packet[3])

class TracePacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.TracePacket, "Error : packet is not a TracePacket"
        l = list(iter(packet))

        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 5, "Error: No valid trace packet"
        assert list_packet[1] == 2, "Error: list_packet is not a trace packet"

        return datapacket.TracePacket(list_packet[0], list_packet[2], list_packet[3], list_packet[4])

class ModePacketMsgPackSerialization(st.Serialization):

    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.ModePacket, "Error : packet is not a ModePacket"
        l = list(iter(packet))

        return list(iter(packet))
    
    @staticmethod
    def unpack(list_packet):
        assert len(list_packet) == 3, "Error: No valid mode packet"
        assert list_packet[1] == 3, "Error: list_packet is not a mode packet"

        return datapacket.ModePacket(list_packet[0], list_packet[2])


# { ptype : SerializationClass, ... }
# choose_serialization.get(ptype) -> return: ptype pack/unpack method
choose_serialization = {
                        1: AckPacketMsgPackSerialization,
                        2: TracePacketMsgPackSerialization,
                        3: ModePacketMsgPackSerialization
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
