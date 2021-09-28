
import bpy
from drone_control import sceneModel
from .planEditor import PlanEditor
from . import droneControlObserver
from drone_control.utilsAlgorithm import MarvelmindHandler
from .droneMovementHandler import DroneMovementHandler
import logging

class PositioningSystemModalOperator(bpy.types.Operator):
    bl_idname = "wm.positioning_system_modal"
    bl_label = "Positioning System Modal"

    isRunning = False

    _timer = None
    _observer = None
    _notifier = None

    def check(self, context):
        return True
    
    @classmethod
    def poll(cls, context):
        return sceneModel.dronesCollection.DronesCollection().getActive() is not None \
               and not PositioningSystemModalOperator.isRunning

    def _observe_drone(self):
        DroneMovementHandler().init()
        DroneMovementHandler().start_positioning()

    def _des_observe_drone(self):
        DroneMovementHandler().stop_positioning()
        DroneMovementHandler().finish()

    def _begin_thread(self, dev):
        handler = MarvelmindHandler()
        handler.start(device=dev, verbose=True)
        # PositioningSystemModalOperator._marvelmind_thread = MarvelmindThread(device=dev, verbose=True)
        # PositioningSystemModalOperator._marvelmind_thread.start()
    
    def _end_thread(self):
        # PositioningSystemModalOperator._marvelmind_thread.stop()
        # PositioningSystemModalOperator._marvelmind_thread.join()
        handler = MarvelmindHandler()
        handler.stop()
    
    def cancel(self, context):
        self._des_observe_drone()

        self._end_thread()

    def _move_drone(self):
        drone = sceneModel.DronesCollection().getActive()

        addr = drone.address
        # beacon = PositioningSystemModalOperator._marvelmind_thread.getBeacon(addr)
        beacon = MarvelmindHandler().getBeacon(addr)

        if beacon is not None:
            pose = sceneModel.Pose(beacon.x, beacon.y, beacon.z, 0, 0, 0)
            # self._notifier.notifyAll(pose)
            DroneMovementHandler().notifyAll(pose)
    
    def modal(self, context, event):
        if event.type == "TIMER":
            
            if not PositioningSystemModalOperator.isRunning:
                self.cancel(context)
                return {'FINISHED'}
            
            if PositioningSystemModalOperator.isRunning:
                self._move_drone()
            
        return {'PASS_THROUGH'}

    def execute(self, context):
        # Genera drone
        # Genera Notifier y observer
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__.split(".")[0]].preferences
        dev = context.scene.prop_marvelmind_port

        self._begin_thread(dev)
        self._observe_drone()

        wm = context.window_manager
        wm.modal_handler_add(self)
        self._timer = wm.event_timer_add(0.1, window=context.window)
        PositioningSystemModalOperator.isRunning = True
        
        return {'RUNNING_MODAL'}


class TogglePositioningSystemOperator(bpy.types.Operator):
    bl_idname = "object.togglepositioningsystem"
    bl_label = "TogglePositioningSystem"

    def _check_serial(self, dev):
        import serial
        
        isvalid = False
        try:
            port = serial.Serial(dev)
            if port.is_open:
                port.close()
            isvalid = True
        except Exception as ex:
            isvalid = False
        return isvalid

    @classmethod
    def poll(cls, context):
        return not PlanEditor().isActive and \
                  sceneModel.dronesCollection.DronesCollection().getActive() is not None

    def execute(self, context):
        if PositioningSystemModalOperator.isRunning:
            PositioningSystemModalOperator.isRunning = False
        else:
            preferences = context.preferences
            addon_prefs = preferences.addons[__name__.split(".")[0]].preferences
            dev = context.scene.prop_marvelmind_port
            
            isValid = self._check_serial(dev)
            if isValid:
                bpy.ops.wm.positioning_system_modal('INVOKE_DEFAULT')
                logger = logging.getLogger("myblenderlog")
                logger.info("positioning_system_modal invoked")
            else:
                self.report({'ERROR'}, f"{dev} device not available")
                logger = logging.getLogger("myblenderlog")
                logger.info("{dev} device not available")
        return {'FINISHED'}
