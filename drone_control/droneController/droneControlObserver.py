
from drone_control.patternModel.observerModel import Notifier, Observer
from drone_control.sceneModel.dronesCollection import DronesCollection

class DroneMovementNotifier(Notifier):

    def __init__(self):
        self.__observers = []

    def attach(self, observer: Observer):
        self.__observers.append(observer)

    def detach(self, observer: Observer):
        self.__observers.remove(observer)
    
    def notifyAll(self, pose, speed):
        for obs in self.__observers:
            obs.notify(pose, speed)

class DroneControlObserver(Observer):

    def notify(self, pose, speed):
        activeDrone = DronesCollection().getActive()
        if activeDrone is not None:
            # TODO: Apply only if pose changed
            activeDrone.translate(pose)
