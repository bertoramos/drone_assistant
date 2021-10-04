import bpy

import socket
import time

from drone_control.patternModel import Singleton
from drone_control.patternModel.stopThread import StoppableThread

from . import msgpack_serialization as ms
from . import datapacket as dp

class Buffer(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.__buffer = []
        self.__last_trace = None
        self.last_rcv_pid = -1
        self.last_snt_pid = -1
    
    def set_packet(self, packet):
        if packet.pid > self.last_rcv_pid:
            if type(packet) == dp.TracePacket:
                self.__last_trace = packet
            else:
                self.__buffer.append(packet)
            self.last_rcv_pid = packet.pid
    
    def clear(self):
        self.__buffer.clear()
        self.__last_trace = None
        self.last_rcv_pid = -1
        self.last_snt_pid = -1
    
    def get_last_trace(self):
        return self.__last_trace

buffersize = 4096

class UDPServer(StoppableThread):

    ack_packets = {}

    def __init__(self, *args, **kwargs):
        self.__clientAddr = kwargs['clientAddr']
        self.__serverAddr = kwargs['serverAddr']
        del kwargs['clientAddr']
        del kwargs['serverAddr']

        super(UDPServer, self).__init__(*args, **kwargs)

        self.__client_socket = None
    
    def __open_socket(self):
        self.__client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.__client_socket.bind(self.__clientAddr)
        self.__client_socket.settimeout(3)
    
    def __close_socket(self):
        if self.__client_socket is not None:
            self.__client_socket.close()
            self.__client_socket = None
            Buffer().clear()
    
    def send(self, packet):
        self.__client_socket.sendto(ms.MsgPackSerializator.pack(packet), self.__serverAddr)
    
    def __receive(self):
        msgFromServer, addr = self.__client_socket.recvfrom(buffersize)
        packet = ms.MsgPackSerializator.unpack(msgFromServer)
        
        Buffer().set_packet(packet)

        if type(packet) in UDPServer.ack_packets:
            Buffer().last_snt_pid += 1
            pid = Buffer().last_snt_pid
            ack_pid = packet.pid
            status = 0
            ackpacket = dp.AckPacket(pid, ack_pid, status)
            self.send(ackpacket)
        
    def run(self):
        try:
            self.__open_socket()
        except Exception as e:
            print(e)
            return
        
        while True:
            if self.stopped():
                break
            try:
                self.__receive()
            except Exception as e:
                print(e)
        try:
            self.__close_socket()
        except Exception as e:
            print(e)


class ConnectionHandler(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.__thread = None
        self.__serverAddr = None
        self.__clientAddr = None
    
    def initialize(self, clientAddr, serverAddr):
        self.__serverAddr = serverAddr
        self.__clientAddr = clientAddr
        self.__thread = UDPServer(serverAddr=self.__serverAddr, clientAddr=self.__clientAddr)
    
    def start(self):
        if self.__thread is not None:
            self.__thread.start()
    
    def stop(self):
        if self.__thread is not None and not self.__thread.stopped():
            self.__thread.stop()
            self.__thread.join()
            self.__thread = None
    
    def send(self, packet):
        if self.__thread is not None and not self.__thread.stopped():
            self.__thread.send(packet)
