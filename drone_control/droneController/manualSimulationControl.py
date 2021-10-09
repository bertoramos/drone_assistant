
import bpy
from math import pi
from mathutils import Euler

from drone_control import sceneModel
from . import droneControlObserver
from . import planExecutionControl
from .droneMovementHandler import DroneMovementHandler

def register():
    pass

def unregister():
    pass

# TODO: Añadir vectores en direcciones adelante, derecha y arriba
# TODO: Aplicar rotaciones a vectores cuando se aplique al drone una rotacion
# TODO: Considerar avance del robot segun los vectores
# TODO: Buscar si en blender se puede mover un objeto segun los ejes LOCALES

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
    
    def _des_observe_drone(self):
        DroneMovementHandler().stop_plan()
        DroneMovementHandler().stop_positioning()
        DroneMovementHandler().finish()
    
    def _apply_move(self, keyname):
        speed = 0.1 # desplazamiento
        # tecla : ('eje')

        action = {'W': ('y', +1),
                  'S': ('y', -1),
                  'D': ('x', +1),
                  'A': ('x', -1),
                  'E': ('z', +1),
                  'C': ('z', -1)
                  }
        
        if keyname not in action: return None

        drone = sceneModel.dronesCollection.DronesCollection().getActive()
        current_pose = drone.pose

        axis, direction = action[keyname]

        last_val = getattr(current_pose.location, axis)
        setattr(current_pose.location, axis, last_val+(direction*speed))

        #self._notifier.notifyAll(current_pose)
        DroneMovementHandler().notifyAll(current_pose)
        return {'RUNNING_MODAL'}

    def _apply_rotation(self, keyname):
        angle_speed = 0.3

        action = {'NUMPAD_4': (self.__yaw, +1),
                  'NUMPAD_6': (self.__yaw, -1),
                  'NUMPAD_8': (self.__pitch, +1),
                  'NUMPAD_2': (self.__pitch, -1),
                  'NUMPAD_9': (self.__roll, +1),
                  'NUMPAD_7': (self.__roll, -1)}

        omit = {'NUMPAD_1','NUMPAD_3','NUMPAD_5'}

        if keyname in omit: return {'RUNNING_MODAL'}
        if keyname not in action: return None

        drone = sceneModel.dronesCollection.DronesCollection().getActive()
        current_pose = drone.pose
        
        if keyname == "NUMPAD_4":
            self.__yaw += 1
        
        if keyname == "NUMPAD_6":
            self.__yaw -= 1
        
        if keyname == "NUMPAD_8":
            self.__pitch += 1
        
        if keyname == "NUMPAD_2":
            self.__pitch -= 1
        
        if keyname == "NUMPAD_9":
            self.__roll += 1
        
        if keyname == "NUMPAD_7":
            self.__roll -= 1
        
        rotation_val = Euler((0, 0, 0))
        rotation_val.rotate_axis('Z', self.__yaw)
        rotation_val.rotate_axis('X', self.__pitch)
        rotation_val.rotate_axis('Y', self.__roll)
        
        current_pose.rotation.x = rotation_val.x
        current_pose.rotation.y = rotation_val.y
        current_pose.rotation.z = rotation_val.z

        DroneMovementHandler().notifyAll(current_pose)
        """
        axis, direction = action[keyname]
        last_val = current_pose.rotation

        last_val.rotate_axis(axis, direction*angle_speed)
        
        current_pose.rotation.x = last_val.x
        current_pose.rotation.y = last_val.y
        current_pose.rotation.z = last_val.z

        # self._notifier.notifyAll(current_pose)
        DroneMovementHandler().notifyAll(current_pose)
        """

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
            DroneMovementHandler().autostop()
        
        return {'PASS_THROUGH'}

    def execute(self, context):
        # Genera drone
        # Genera Notifier y observer
        self._observe_drone()
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        ManualSimulationModalOperator.isRunning = True

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self._des_observe_drone()

        ManualSimulationModalOperator.isRunning = False
