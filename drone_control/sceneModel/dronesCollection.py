
from drone_control.patternModel.singletonModel import Singleton

class DronesCollection(metaclass=Singleton):

    def __init__(self):
        self.__droneDict = {}
        self.__activeDroneID = None

    def getActive(self):
        return self.get(self.__activeDroneID)

    def setActive(self, idx):
        if idx in self.__droneDict:
            self.__activeDroneID = idx
        else:
            raise Exception(f"{idx} does not exist")

    def removeActive(self):
        self.remove(self.__activeDroneID)
        self.__activeDroneID = None

    def unsetActive(self):
        self.__activeDroneID = None

    def add(self, obj):
        self.__droneDict[obj.meshID] = obj

    def get(self, idx):
        if idx in self.__droneDict:
            return self.__droneDict[idx]
        return None

    def remove(self, idx):
        if idx in self.__droneDict:
            del self.__droneDict[idx]
        if self.__activeDroneID == idx:
            self.__activeDroneID = None

    def __len__(self):
        return len(self.__droneDict)

    def __iter__(self):
        self.__n = 0
        return self

    def __next__(self):
        if self.__n < len(self.__droneDict):
            keys = list(self.__droneDict.keys())
            result = (keys[self.__n], self.__droneDict[keys[self.__n]])
            self.__n += 1
            return result
        else:
            self.__n = -1
            raise StopIteration

    activeDrone = property(fget=getActive, fset=setActive)
