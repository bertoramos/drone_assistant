
import bpy

from drone_control.patternModel.observerModel import Notifier, Observer
from drone_control.sceneModel import DronesCollection, PlanCollection, DroneModel

from .hudWriter import HUDWriterOperator, Texto, TextColor

class PlanControllerObserver(Observer):

    def __init__(self):
        self.__current_plan = None
        self.__next_pose = None
        self.__next_pose_id = -1
        self.__stopped = True
    
    def _show_info(self, pose):
        loc_dist = pose.get_location_distance(self.__next_pose)
        rot_dist = pose.get_rotation_distance(self.__next_pose)
        txt = Texto()
        txt.text = f"next_pose={self.__next_pose_id} {loc_dist = :0.4f} meters and {rot_dist = :0.4f} degrees"
        HUDWriterOperator._textos['PLAN_EXECUTION_INFO'] = txt

        self.__current_plan.highlight(self.__next_pose_id)
    
    def _clear_info(self):
        del HUDWriterOperator._textos['PLAN_EXECUTION_INFO']
        self.__current_plan.no_highlight()

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

        self._show_info(DronesCollection().getActive().pose)
    
    def stop(self):
        self.__stopped = True
        print("STOP PLAN EXECUTION")
    
    def stopped(self):
        return self.__stopped
    
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
                self._show_info(pose)
            else:
                self._clear_info()
                self.stop()
                return
        else:
            self._show_info(pose)

            print(f"next_pose={self.__next_pose} {loc_dist = :0.4f} meters and {rot_dist = :0.4f} degrees")
