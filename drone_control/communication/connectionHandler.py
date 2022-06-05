import bpy

import socket
import time

from drone_control.patternModel import Singleton
from drone_control.patternModel.stopThread import StoppableThread
from drone_control.utilsAlgorithm import FPSCounter
from drone_control.sceneModel.dronesCollection import DronesCollection

from . import msgpack_serialization as ms
from . import datapacket as dp

class Buffer(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.__buffer = []
        self.last_rcv_pid = 0
        self.last_snt_pid = 0
    
    def set_packet(self, packet):
        if packet.pid > self.last_rcv_pid:
            self.__buffer.append(packet)
            self.last_rcv_pid = packet.pid
    
    def clear(self):
        self.__buffer.clear()
        self.last_rcv_pid = 0
        self.last_snt_pid = 0
    
    def get_ack_packet(self, pid):
        ret_packet = None
        for packet in self.__buffer:
            if type(packet) == dp.AckPacket and packet.ackPid == pid:
                ret_packet = packet
                break
        if ret_packet is not None:
            self.__buffer.remove(ret_packet)
        return ret_packet
    
    def receive_end_capture(self):
        ret_packet = None
        for packet in self.__buffer:
            if type(packet) == dp.EndCapturePacket:
                ret_packet = packet
                break
        if ret_packet is not None:
            self.__buffer.remove(ret_packet)
        return ret_packet
    
    def receive_close_server(self):
        ret_packet = None
        for packet in self.__buffer:
            if type(packet) == dp.CloseServerPacket:
                ret_packet = packet
                break
        if ret_packet is not None:
            self.__buffer.remove(ret_packet)
        return ret_packet
    
    def __iter__(self):
        return iter(self.__buffer)

buffersize = 4096

class UDPServer(StoppableThread):

    ack_packets = { dp.CloseServerPacket }

    def __init__(self, *args, **kwargs):
        self.__clientAddr = kwargs['clientAddr']
        self.__serverAddr = kwargs['serverAddr']
        del kwargs['clientAddr']
        del kwargs['serverAddr']

        super(UDPServer, self).__init__(*args, **kwargs)

        self.__client_socket = None

        try:
            self.__open_socket()
        except Exception as e:
            print(e)
            return
    
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
        #print("Received : ", list(iter(packet)))
        Buffer().set_packet(packet)
        
        if type(packet) in UDPServer.ack_packets:
            Buffer().last_snt_pid += 1
            pid = Buffer().last_snt_pid
            ack_pid = packet.pid
            status = dp.AckPacket.STATUS_OK
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
                import sys, os
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                #import traceback
                #print(traceback.format_exc())
                #print(e, type(e), "Line: ", exc_tb.tb_lineno, " ", fname, " ", exc_type)
                #if type(e) == socket.timeout:
                #    no_recv_num -=1
                #    if no_recv_num == 0:
                #        break
        
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
        self.__isConnected = False
    
    def initialize(self, clientAddr, serverAddr):
        try:
            self.__serverAddr = serverAddr
            self.__clientAddr = clientAddr
            self.__thread = UDPServer(serverAddr=self.__serverAddr, clientAddr=self.__clientAddr)
        except Exception as ex:
            print(ex)
            return False
        return True

    def start(self):
        if self.__thread is not None:
            self.__thread.start()
            self.__isConnected = True
    
    def stop(self):
        if self.__thread is not None and not self.__thread.stopped():
            self.__thread.stop()
            self.__thread.join()
            self.__thread = None
            self.__isConnected = False
    
    def __get_connected(self):
        return self.__isConnected
    
    connected = property(fget=__get_connected)
    
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
    
    def send_start_capture(self):
        Buffer().last_snt_pid += 1
        PID = Buffer().last_snt_pid

        start_capture_packet = dp.StartCapturePacket(PID)
        self.send(start_capture_packet)
        
        print("Sent : ", list(iter(start_capture_packet)))
        
        return self.receive_ack_packet(PID)
    
    def send_stop_capture(self):
        Buffer().last_snt_pid += 1
        PID = Buffer().last_snt_pid

        end_capture_packet = dp.EndCapturePacket(PID)
        self.send(end_capture_packet)
        
        print("Sent : ", list(iter(end_capture_packet)))
        
        return self.receive_ack_packet(PID)
    
    def receive_close_server(self):
        return Buffer().receive_close_server() is not None
    
    def send_pose(self, timestamp, x, y, z, yaw):
        Buffer().last_snt_pid += 1
        PID = Buffer().last_snt_pid

        pose_packet = dp.PosePacket(PID, timestamp, x, y, z, yaw)
        self.send(pose_packet)

        return True
