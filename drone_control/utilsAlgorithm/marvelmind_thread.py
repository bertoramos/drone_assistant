
import threading
import marvelmind_pylib as mpl
from dataclasses import dataclass
from drone_control.patternModel import Singleton, StoppableThread

from .fps_counter import FPSCounter

from mathutils import Vector

import logging

@dataclass
class Beacon:
    address: int

    timestamp: float

    x: float
    y: float
    z: float

    angle: float

    is_stationary: bool

    speed: float = 0.0

class MarvelmindThread(StoppableThread):
    
    def __init__(self, *args, **kwargs):
        self.__tty_dev = kwargs['device']
        self.__verbose = kwargs['verbose']
        del kwargs['device']
        del kwargs['verbose']

        super(MarvelmindThread, self).__init__(*args, **kwargs)

        self.__dev = mpl.MarvelMindDevice(self.__tty_dev, self.__verbose)
        self.__dev.start()
        
        self.__beacons = {}
    
    def execute(self):
        logger = logging.getLogger("myblenderlog")
        
        mobile_pos = self.__dev.getMobileBeaconsPosition()
        stationary_pos = self.__dev.getStationaryBeaconsPosition()

        if len(mobile_pos) > 0:
            FPSCounter().notifyPositionChange()

        txt = "Get mobile beacon data : "
        for address, xyz in mobile_pos.items():
            
            current_beacon = Beacon(address,
                                    xyz[0],
                                    xyz[1], xyz[2], xyz[3], 
                                    xyz[4],
                                    False)
            
            
            if address in self.__beacons:
                prev_beacon = self.__beacons[address]
                t1 = prev_beacon.timestamp
                t0 = current_beacon.timestamp
                timelen = abs(t0 - t1) / 1000.0
                p1 = Vector((prev_beacon.x, prev_beacon.y, prev_beacon.z))
                p0 = Vector((current_beacon.x, current_beacon.y, current_beacon.z))

                length = (p0 - p1).length

                if timelen > 0:
                    current_beacon.speed = length/timelen
            
            self.__beacons[address] = current_beacon
            txt += "[" + str(address) + " : " + str(xyz) + "] "
        # if len(mobile_pos) > 0: logger.info(txt)
        
        txt = "Get stationary beacon data : "
        for address, xyz in stationary_pos.items():
            current_beacon = Beacon(address,
                                    0,
                                    xyz[0], xyz[1], xyz[2], 
                                    0,
                                    True)
            
            self.__beacons[address] = current_beacon
            txt += "[" + str(address) + " : " + str(xyz) + "] "

        logger.info(txt)
        # if len(stationary_pos)>0: logger.info(txt)
    

    def getBeacon(self, address):
        return self.__beacons[address] if address in self.__beacons else None
    
    def getAll(self):
        return self.__beacons

    def getStationaryBeacons(self):
        return [self.__beacons[addr] for addr in list(self.__beacons) if self.__beacons[addr].is_stationary]
    
    def __str__(self):
        txt = ""
        for address in list(self.__beacons):
            pos = self.__beacons[address]
            txt += str(pos) + "\n"
        return txt
    
    def close_device(self):
        self.__dev.close()
        del self.__dev

    def run(self):
        logger = logging.getLogger("myblenderlog")
        logger.info("Marvelmind thread started")
        
        while True:
            if self.stopped():
                self.close_device()
                logger.info("Marvelmind thread stopped")
                return
            self.execute()

class MarvelmindHandler(metaclass=Singleton):

    def __init__(self):
        self.__thread = None
    
    def start(self, device, verbose):
        if self.__thread is None:
            self.__thread = MarvelmindThread(device=device, verbose=verbose)
            self.__thread.start()
    
    def stop(self):
        if self.__thread is not None and not self.__thread.stopped():
            self.__thread.stop()
            self.__thread.join()
            self.__thread = None
        else:
            raise Exception("Thread is not started")
    
    def getBeacon(self, address):
        if self.__thread is not None:
            return self.__thread.getBeacon(address=address)
        else:
            raise Exception("Thread is not started")
    
    def getAll(self):
        if self.__thread is not None:
            return self.__thread.getAll()
        else:
            raise Exception("Thread is not started")
    
    def getStationaryBeacons(self):
        if self.__thread is not None:
            return self.__thread.getStationaryBeacons()
        else:
            raise Exception("Thread is not started")
    
    def isRunning(self):
        return self.__thread is not None
