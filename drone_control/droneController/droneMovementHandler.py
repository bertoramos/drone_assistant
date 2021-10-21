
from drone_control.patternModel import Singleton
from .planExecutionControl import PlanControllerObserver
from .droneControlObserver import DroneControlObserver, DroneMovementNotifier

class DroneMovementHandler(metaclass=Singleton):
    
    def __init__(self):
        self._notifier = None
        self._positioning_observer = None
        self._plan_control_observer = None

    def init(self):
        if self._notifier is None:
            self._notifier = DroneMovementNotifier()
    
    def finish(self):
        if self._notifier is not None:
            self._detach_all()
            self._notifier = None
    
    def _detach_all(self):
        if self._notifier is not None:
            if self._positioning_observer is not None:
                self._notifier.detach(self._positioning_observer)
                self._positioning_observer = None
            
            if self._plan_control_observer is not None:
                self._notifier.detach(self._positioning_observer)
                self._positioning_observer = None

    def _attach_observer(self, observer):
        if self._notifier is not None:
            self._notifier.attach(observer)
    
    def _detach_observer(self, observer):
        if self._notifier is not None:
            self._notifier.detach(observer)
    
    def start_positioning(self):
        if self._positioning_observer is None:
            self._positioning_observer = DroneControlObserver()
            self._attach_observer(self._positioning_observer)

    def stop_positioning(self):
        if self._positioning_observer is not None:
            self._detach_observer(self._positioning_observer)
            self._positioning_observer = None
    
    def notifyAll(self, pose, speed):
        self._notifier.notifyAll(pose, speed)
    
    def start_plan(self):
        if self._plan_control_observer is None:
            self._plan_control_observer = PlanControllerObserver()
            self._attach_observer(self._plan_control_observer)
            self._plan_control_observer.start()
    
    def stop_plan(self):
        if self._notifier is not None and self._plan_control_observer is not None:
            self._plan_control_observer.stop()
            self._notifier.detach(self._plan_control_observer)
            self._plan_control_observer = None
    
    def autostop(self):
        if self._plan_control_observer is not None:
            if self._plan_control_observer.stopped():
                self.stop_plan()
    
    def isPositioningRunning(self):
        return self._positioning_observer is not None

    def isPlanRunning(self):
        if self._plan_control_observer is not None:
            return not self._plan_control_observer.stopped()
        else:
            return False
    
    def show_current_level_mode(self, mode):
        self._plan_control_observer.show_current_level_mode(mode)
    
