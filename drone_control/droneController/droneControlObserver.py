
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
            loc_dist = pose.get_location_distance(activeDrone.pose)
            #rot_dist = pose.get_rotation_distance(activeDrone.pose)
            rx_dif = abs(pose.rotation.x - activeDrone.pose.rotation.x)
            ry_dif = abs(pose.rotation.y - activeDrone.pose.rotation.y)
            rz_dif = abs(pose.rotation.z - activeDrone.pose.rotation.z)

            EPS = 0.01
            if loc_dist > EPS or rx_dif > EPS or ry_dif > EPS or rz_dif > EPS:
                activeDrone.translate(pose)
