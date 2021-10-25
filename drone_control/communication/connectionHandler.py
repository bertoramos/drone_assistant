import bpy

import socket
import time

from drone_control.patternModel import Singleton
from drone_control.patternModel.stopThread import StoppableThread
from drone_control.utilsAlgorithm import FPSCounter

from . import msgpack_serialization as ms
from . import datapacket as dp

class Buffer(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.__buffer = []
        self.__last_trace = None
        self.last_rcv_pid = 0
        self.last_snt_pid = 0
    
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
        self.last_rcv_pid = 0
        self.last_snt_pid = 0
    
    def get_last_trace(self):
        return self.__last_trace
    
    def get_ack_packet(self, pid):
        ret_packet = None
        for packet in self.__buffer:
            if type(packet) == dp.AckPacket and packet.ackPid == pid:
                ret_packet = packet
                break
        if ret_packet is not None:
            self.__buffer.remove(ret_packet)
        return ret_packet
    
    def __iter__(self):
        return iter(self.__buffer)

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

        self.__open_socket()    
    
    def __open_socket(self):
        self.__client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.__client_socket.bind(self.__clientAddr)
        self.__client_socket.settimeout(3)
    
    def __close_socket(self):
        if self.__client_socket is not None:
            self.__client_socket.close()
            self.__client_socket = None
            Buffer().clear()
    
    def __del__(self):
        self.__close_socket()
    
    def send(self, packet):
        if self.__client_socket is not None:
            self.__client_socket.sendto(ms.MsgPackSerializator.pack(packet), self.__serverAddr)
    
    def __receive(self):
        msgFromServer, addr = self.__client_socket.recvfrom(buffersize)
        packet = ms.MsgPackSerializator.unpack(msgFromServer)
        if packet is not None and type(packet) != dp.TracePacket:
            print("Received : ", list(iter(packet)))
        Buffer().set_packet(packet)


        if type(packet) == dp.TracePacket:
            FPSCounter().notifyRotationChange()

        if type(packet) in UDPServer.ack_packets:
            Buffer().last_snt_pid += 1
            pid = Buffer().last_snt_pid
            ack_pid = packet.pid
            status = 0
            ackpacket = dp.AckPacket(pid, ack_pid, status)
            self.send(ackpacket)
        
    def run(self):

        from drone_control.droneController import PositioningSystemModalOperator
        
        MAX_TIMEOUT = 5
        no_recv_num = MAX_TIMEOUT
        while True:
            if self.stopped():
                break
            try:
                self.__receive()
                no_recv_num = MAX_TIMEOUT
            except Exception as e:
                print(e, type(e))
                if type(e) == socket.timeout:
                    no_recv_num -=1
                    if no_recv_num == 0:
                        break
        
        PositioningSystemModalOperator.isRunning = False
        
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
        try:
            self.__serverAddr = serverAddr
            self.__clientAddr = clientAddr
            self.__thread = UDPServer(serverAddr=self.__serverAddr, clientAddr=self.__clientAddr)
        except Exception as ex:
            return False
        return True
    
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
    
    def receive_ack_packet(self, pid):
        start_time = time.time()
        ack_packet = None
        while abs(time.time() - start_time) < 8.0 and ack_packet is None:
            ack_packet = Buffer().get_ack_packet(pid)
        return ack_packet
    
    def send_change_mode(self, mode):
        Buffer().last_snt_pid += 1
        PID = Buffer().last_snt_pid
        mode_packet = dp.ModePacket(PID, mode)
        self.send(mode_packet)
        print("Sent : ", list(iter(mode_packet)))
        return self.receive_ack_packet(PID)
