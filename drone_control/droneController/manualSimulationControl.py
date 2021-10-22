
import bpy
from math import pi, cos, sin
from mathutils import Euler, Vector, Matrix

from drone_control import sceneModel
from . import droneControlObserver
from . import planExecutionControl
from .droneMovementHandler import DroneMovementHandler

def register():
    pass

def unregister():
    pass

def rotateAround(v1, angle, axis):
    l = axis.x
    m = axis.y
    n = axis.z

    m = Matrix((
            ( l*l*(1-cos(angle)) + 1*cos(angle), m*l*(1-cos(angle)) - n*sin(angle), n*l*(1-cos(angle)) + m*sin(angle) ),
            ( l*m*(1-cos(angle)) + n*sin(angle), m*m*(1-cos(angle)) + 1*cos(angle), n*m*(1-cos(angle)) - l*sin(angle) ),
            ( l*n*(1-cos(angle)) - m*sin(angle), m*n*(1-cos(angle)) + l*sin(angle), n*n*(1-cos(angle)) + 1*cos(angle) )
            ))
    
    return m @ v1


class ManualSimulationModalOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "scene.manual_simulation_modal_operator"
    bl_label = "Manual Simulation System"

    _timer = None

    isRunning = False

    @classmethod
    def poll(cls, context):
        return sceneModel.dronesCollection.DronesCollection().getActive() is not None \
                and not ManualSimulationModalOperator.isRunning

    def _observe_drone(self):
        DroneMovementHandler().init()
        DroneMovementHandler().start_positioning()
        self.__yaw = 0
        self.__pitch = 0
        self.__roll = 0
        self.__forward = Vector((0, 1, 0))
        self.__right = Vector((1, 0, 0))
        self.__up = Vector((0, 0, 1))
        self.__speed = 0

        self.__current_pose = sceneModel.dronesCollection.DronesCollection().getActive().pose
    
    def _des_observe_drone(self):
        DroneMovementHandler().stop_plan()
        DroneMovementHandler().stop_positioning()
        DroneMovementHandler().finish()
    
    def _apply_move(self, keyname):
        speed = 0.1 # desplazamiento
        # tecla : ('eje')

        action = {'W': (self.__forward, +1),
                  'S': (self.__forward, -1),
                  'D': (self.__right, +1),
                  'A': (self.__right, -1),
                  'E': (self.__up, +1),
                  'C': (self.__up, -1)
                  }
        
        if keyname not in action: return None

        drone = sceneModel.dronesCollection.DronesCollection().getActive()
        current_pose = drone.pose

        axis, direction = action[keyname]

        current_pose.location.x += direction * speed * axis.x
        current_pose.location.y += direction * speed * axis.y
        current_pose.location.z += direction * speed * axis.z
        
        self.__current_pose = current_pose

        #DroneMovementHandler().notifyAll(current_pose, self.__speed)
        return {'RUNNING_MODAL'}

    def _apply_rotation(self, keyname):
        angle_step = pi/4
        
        action = {'NUMPAD_4': (+1, self.__up, angle_step, 0, 0), # rotate left
                  'NUMPAD_6': (-1, self.__up, angle_step, 0, 0), # rotate right
                  'NUMPAD_8': (+1, self.__right, 0, angle_step, 0), # rotate up
                  'NUMPAD_2': (-1, self.__right, 0, angle_step, 0), # rotate down
                  'NUMPAD_9': (-1, self.__forward, 0, 0, angle_step), # roll right
                  'NUMPAD_7': (+1, self.__forward, 0, 0, angle_step)  # roll left
                  }

        omit = {'NUMPAD_1','NUMPAD_3','NUMPAD_5'}

        if keyname in omit: return {'RUNNING_MODAL'}
        if keyname not in action: return None

        drone = sceneModel.dronesCollection.DronesCollection().getActive()
        current_pose = drone.pose
        
        dir, axis, yaw_diff, pitch_diff, roll_diff = action[keyname]
        self.__forward = rotateAround(self.__forward, dir*angle_step, axis)
        self.__right = rotateAround(self.__right, dir*angle_step, axis)
        self.__up = rotateAround(self.__up, dir*angle_step, axis)

        self.__yaw   += dir*yaw_diff
        self.__pitch += dir*pitch_diff
        self.__roll  += dir*roll_diff
        
        rotation_val = Euler((0, 0, 0))
        rotation_val.rotate_axis('Z', self.__yaw)
        rotation_val.rotate_axis('X', self.__pitch)
        rotation_val.rotate_axis('Y', self.__roll)
        
        current_pose.rotation.x = rotation_val.x
        current_pose.rotation.y = rotation_val.y
        current_pose.rotation.z = rotation_val.z

        self.__current_pose = current_pose

        #DroneMovementHandler().notifyAll(current_pose, self.__speed)
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.value == 'PRESS':
            if ( rescode := self._apply_move(event.type) ) is not None:
                return rescode
            if ( rescode := self._apply_rotation(event.type) ) is not None:
                return rescode
        
        if event.type == "TIMER":
            DroneMovementHandler().notifyAll(self.__current_pose, self.__speed)
            DroneMovementHandler().autostop()
        
        return {'PASS_THROUGH'}

    def execute(self, context):
        # Genera drone
        # Genera Notifier y observer
        self._observe_drone()
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        ManualSimulationModalOperator.isRunning = True

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self._des_observe_drone()

        ManualSimulationModalOperator.isRunning = False
