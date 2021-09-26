
import bpy
from drone_control.patternModel.observerModel import Notifier, Observer
from drone_control.sceneModel import DronesCollection, PlanCollection, DroneModel

class PlanControllerObserver(Observer):

    def __init__(self):
        self.__current_plan = None
        self.__next_pose = None
        self.__next_pose_id = -1
        self.__stopped = True

    def start(self):
        if not self.__stopped:
            return

        self.__current_plan = PlanCollection().getActive()
        
        if self.__current_plan is None:
            self.stop()
            return

        self.__next_pose_id = 0
        if self.__next_pose_id >= len(list(iter(self.__current_plan))):
            self.stop()
            return
        
        self.__next_pose = self.__current_plan.getPose(self.__next_pose_id)
        self.__stopped = False
        print("START PLAN EXECUTION")
    
    def stop(self):
        self.__stopped = True
        print("STOP PLAN EXECUTION")
    
    def notify(self, pose):
        print("notify")
        if self.__stopped:
            return
        
        loc_dist = pose.get_location_distance(self.__next_pose)
        rot_dist = pose.get_rotation_distance(self.__next_pose)
        
        EPS = 0.1 # bpy.context.scene.TOL
        if loc_dist < EPS and rot_dist < EPS:
            if self.__next_pose_id + 1 < len(list(iter(self.__current_plan))):
                self.__next_pose_id += 1
                self.__next_pose = self.__current_plan.getPose(self.__next_pose_id)
                print("New pose")
            else:
                self.stop()
                return
        else:
            print(f"next_pose={self.__next_pose} {loc_dist = } meters and {rot_dist = } degrees")

