
import threading
import marvelmind_pylib as mpl
from dataclasses import dataclass
from drone_control.patternModel import Singleton

import logging

@dataclass
class Beacon:
    address: int

    x: float
    y: float
    z: float

    is_stationary: bool

class StoppableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stopper = threading.Event()
    
    def stop(self):
        self._stopper.set()
    
    def stopped(self):
        return self._stopper.isSet()


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

        txt = "Get mobile beacon data : "
        for address, xyz in mobile_pos.items():
            current_beacon = Beacon(address,
                                    xyz[0], xyz[1], xyz[2],
                                    False)
            
            self.__beacons[address] = current_beacon
            txt += "[" + str(address) + " : " + str(xyz) + "] "
        
        # if len(mobile_pos) > 0: logger.info(txt)
        
        txt = "Get stationary beacon data : "
        for address, xyz in stationary_pos.items():
            current_beacon = Beacon(address,
                                    xyz[0], xyz[1], xyz[2],
                                    True)
            
            self.__beacons[address] = current_beacon
            txt += "[" + str(address) + " : " + str(xyz) + "] "
    
        # if len(stationary_pos)>0: logger.info(txt)
    

    def getBeacon(self, address):
        return self.__beacons[address] if address in self.__beacons else None
    
    def getAll(self):
        return self.__beacons

    def getStationaryBeacons(self):
        return [beacon for addr, beacon in self.__beacons.items() if beacon.is_stationary]
    
    def __str__(self):
        txt = ""
        for address, pos in self.__beacons.items():
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
        self.__thread = MarvelmindThread(device=device, verbose=verbose)
        self.__thread.start()
    
    def stop(self):
        if self.__thread is not None:
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