
import bpy
from math import pi

from drone_control import sceneModel
from . import droneControlObserver


def register():
    pass

def unregister():
    pass

class MockDronePosSysModalOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "scene.mock_possys_modal_operator"
    bl_label = "Modal Mock Positioning System"

    _timer = None
    _observer = None
    _notifier = None

    isRunning = False

    @classmethod
    def poll(cls, context):
        return sceneModel.dronesCollection.DronesCollection().getActive() is not None \
                and not MockDronePosSysModalOperator.isRunning

    def _observe_drone(self):
        self._notifier = droneControlObserver.DroneMovementNotifier()
        self._observer = droneControlObserver.DroneControlObserver()

        self._notifier.attach(self._observer)

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

        drone.translate(current_pose)

        return {'RUNNING_MODAL'}

    def _apply_rotation(self, keyname):
        angle_speed = 0.3

        action = {'NUMPAD_4': ('Z', +1),
                  'NUMPAD_6': ('Z', -1),
                  'NUMPAD_8': ('X', +1),
                  'NUMPAD_2': ('X', -1),
                  'NUMPAD_9': ('Y', +1),
                  'NUMPAD_7': ('Y', -1)}

        omit = {'NUMPAD_1','NUMPAD_3','NUMPAD_5'}

        if keyname in omit: return {'RUNNING_MODAL'}
        if keyname not in action: return None

        drone = sceneModel.dronesCollection.DronesCollection().getActive()
        current_pose = drone.pose

        axis, direction = action[keyname]
        last_val = current_pose.rotation

        last_val.rotate_axis(axis, direction*angle_speed)

        current_pose.rotation.x = last_val.x
        current_pose.rotation.y = last_val.y
        current_pose.rotation.z = last_val.z

        drone.translate(current_pose)

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

        return {'PASS_THROUGH'}

    def execute(self, context):
        # Genera drone
        # Genera Notifier y observer
        self._observe_drone()
        wm = context.window_manager
        wm.modal_handler_add(self)
        MockDronePosSysModalOperator.isRunning = True

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self._notifier.detach(self._observer)

        del self._observer
        del self._notifier

        MockDronePosSysModalOperator.isRunning = False
