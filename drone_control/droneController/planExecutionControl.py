
import bpy
from mathutils import Vector

from drone_control.patternModel.observerModel import Notifier, Observer
from drone_control.sceneModel import DronesCollection, PlanCollection, DroneModel

from .hudWriter import Arrow, Curve, DashedCurve, HUDWriterOperator, Point3D, Texto, RGBAColor

class PlanControllerObserver(Observer):

    def __init__(self):
        self.__current_plan = None

        self.__prev_pose = None
        self.__prev_pose_id = -1
        self.__next_pose = None
        self.__next_pose_id = -1
        self.__stopped = True

        self.__speed = 0

        self.__bearing_color = RGBAColor(1.0, 1.0, 1.0, 1.0)
        self.__path_color = RGBAColor(1.0, 0.0, 1.0, 1.0)
        self.__tracking_color = RGBAColor(0.0, 1.0, 1.0, 1.0)
        self.__tracking = DashedCurve([], self.__tracking_color)
        self.__tracking.color = self.__tracking_color
        self.__tracking.scale = 50
    
    def _show_info(self, pose):
        # loc_dist = pose.get_location_distance(self.__next_pose)
        # rot_dist = pose.get_rotation_distance(self.__next_pose)

        xdist = abs(pose.location.x - self.__next_pose.location.x)
        ydist = abs(pose.location.y - self.__next_pose.location.y)
        zdist = abs(pose.location.z - self.__next_pose.location.z)

        # Next pose id
        txt1 = Texto()
        txt1.x = 10
        txt1.y = 80
        txt1.text = f"next_pose={self.__next_pose_id}"
        txt1.text_color = RGBAColor(1., 1., 1., 1.)
        HUDWriterOperator._textos['PLAN_EXECUTION_INFO_1'] = txt1

        # XYZ DISTANCE
        txt2 = Texto()
        txt2.x = 10
        txt2.y = 50
        txt2.text = f"X: {xdist:0.2f} m"
        txt2.text_color = RGBAColor(248./255., 55./255., 82./255., 1.)
        HUDWriterOperator._textos['PLAN_EXECUTION_INFO_2'] = txt2

        txt3 = Texto()
        txt3.x = 150
        txt3.y = 50
        txt3.text = f"Y: {ydist:0.2f} m"
        txt3.text_color = RGBAColor(135./255., 213./255., 18./255., 1.)
        HUDWriterOperator._textos['PLAN_EXECUTION_INFO_3'] = txt3

        txt4 = Texto()
        txt4.x = 300
        txt4.y = 50
        txt4.text = f"Z: {zdist:0.2f} m"
        txt4.text_color = RGBAColor(45./255., 140./255., 248./255., 1.)
        HUDWriterOperator._textos['PLAN_EXECUTION_INFO_4'] = txt4
        
        # Height
        txt5 = Texto()
        txt5.x = 10
        txt5.y = 20
        txt5.text = f"Height: {pose.location.z:0.2f} m | Speed {self.__speed:0.2f} m/s"
        txt5.text_color = RGBAColor(1., 1., 1., 1.)
        HUDWriterOperator._textos['PLAN_EXECUTION_INFO_5'] = txt5

        # Path
        path_curve = Curve([])

        p1 = Point3D(self.__prev_pose.location.x, self.__prev_pose.location.y, self.__prev_pose.location.z)
        path_curve.points.append(p1)

        p2 = Point3D(self.__next_pose.location.x, self.__next_pose.location.y, self.__next_pose.location.z)
        path_curve.points.append(p2)

        path_curve.color = self.__path_color
        HUDWriterOperator._curves_3d['PATH'] = path_curve

        # Tracking
        HUDWriterOperator._dashed_curve_3d['TRACKING'] = self.__tracking

        # Bearing
        if len(self.__tracking.points) >= 2:
            P = self.__tracking.points[-1]
            Q = self.__tracking.points[-2]
            P = Vector((P.x, P.y, P.z))
            Q = Vector((Q.x, Q.y, Q.z))
            v = (Q-P).normalized()
            
            R = P - 0.25*v
            
            arrow = Arrow(Point3D(P.x, P.y, P.z), Point3D(R.x, R.y, R.z), head_len=0.05, head_size=0.02, color=self.__bearing_color)
            HUDWriterOperator._arrows_3d['BEARING'] = arrow

        self.__current_plan.highlight(self.__next_pose_id)
    
    def _clear_info(self):
        if 'PLAN_EXECUTION_INFO_1' in HUDWriterOperator._textos:
            del HUDWriterOperator._textos['PLAN_EXECUTION_INFO_1']
        
        if 'PLAN_EXECUTION_INFO_2' in HUDWriterOperator._textos:
            del HUDWriterOperator._textos['PLAN_EXECUTION_INFO_2']
        
        if 'PLAN_EXECUTION_INFO_3' in HUDWriterOperator._textos:
            del HUDWriterOperator._textos['PLAN_EXECUTION_INFO_3']
        
        if 'PLAN_EXECUTION_INFO_4' in HUDWriterOperator._textos:
            del HUDWriterOperator._textos['PLAN_EXECUTION_INFO_4']
        
        if 'PLAN_EXECUTION_INFO_5' in HUDWriterOperator._textos:
            del HUDWriterOperator._textos['PLAN_EXECUTION_INFO_5']
        
        if 'PATH' in HUDWriterOperator._curves_3d:
            del HUDWriterOperator._curves_3d['PATH']
        
        if 'TRACKING' in HUDWriterOperator._dashed_curve_3d:
            del HUDWriterOperator._dashed_curve_3d['TRACKING']
        
        if 'BEARING' in HUDWriterOperator._arrows_3d:
            del HUDWriterOperator._arrows_3d['BEARING']
        
        self.__current_plan.no_highlight()

    def start(self):
        if not self.__stopped:
            return

        self.__current_plan = PlanCollection().getActive()
        
        if self.__current_plan is None:
            self.stop()
            return
        
        self.__prev_pose_id = -1
        self.__next_pose_id = 0
        if self.__next_pose_id >= len(list(iter(self.__current_plan))):
            self.stop()
            return
        
        self.__prev_pose = self.__current_plan.getPose(self.__prev_pose_id) if self.__prev_pose_id > 0 else DronesCollection().activeDrone.pose
        self.__next_pose = self.__current_plan.getPose(self.__next_pose_id)
        self.__stopped = False
        print("START PLAN EXECUTION")

        self._show_info(DronesCollection().getActive().pose)
    
    def stop(self):
        self.__stopped = True
        self._clear_info()
        print("STOP PLAN EXECUTION")
    
    def stopped(self):
        return self.__stopped
    
    def notify(self, pose, speed):
        print("notify")
        if self.__stopped:
            return
        
        loc_dist = pose.get_location_distance(self.__next_pose)
        rot_dist = pose.get_rotation_distance(self.__next_pose)

        self.__speed = speed
        
        EPS = 0.1 # bpy.context.scene.TOL
        if loc_dist < EPS and rot_dist < EPS:
            if self.__next_pose_id + 1 < len(list(iter(self.__current_plan))):
                self.__prev_pose_id += 1
                self.__next_pose_id += 1
                self.__prev_pose = self.__current_plan.getPose(self.__prev_pose_id)
                self.__next_pose = self.__current_plan.getPose(self.__next_pose_id)

                self.__tracking.points.clear()
                print("New pose")
                self._show_info(pose)
            else:
                self._clear_info()
                self.stop()
                return
        else:
            p = Point3D(pose.location.x, pose.location.y, pose.location.z)
            self.__tracking.points.append(p)
            self._show_info(pose)

            print(f"next_pose={self.__next_pose} {loc_dist = :0.4f} meters and {rot_dist = :0.4f} degrees")
