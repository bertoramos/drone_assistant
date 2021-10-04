
import bpy
from mathutils import Euler
import logging

from drone_control.communication import Buffer, ConnectionHandler
from drone_control import sceneModel
from .planEditor import PlanEditor
from drone_control.utilsAlgorithm import MarvelmindHandler
from .droneMovementHandler import DroneMovementHandler


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

    def _begin_thread(self, dev, clientAddr, serverAddr):
        handler = MarvelmindHandler()
        handler.start(device=dev, verbose=True)
        ConnectionHandler().initialize(clientAddr, serverAddr)
        ConnectionHandler().start()
        # PositioningSystemModalOperator._marvelmind_thread = MarvelmindThread(device=dev, verbose=True)
        # PositioningSystemModalOperator._marvelmind_thread.start()
    
    def _end_thread(self):
        # PositioningSystemModalOperator._marvelmind_thread.stop()
        # PositioningSystemModalOperator._marvelmind_thread.join()
        handler = MarvelmindHandler()
        handler.stop()
        ConnectionHandler().stop()
    
    def cancel(self, context):
        self._des_observe_drone()

        self._end_thread()

    def _move_drone(self):
        drone = sceneModel.DronesCollection().getActive()

        addr = drone.address
        # beacon = PositioningSystemModalOperator._marvelmind_thread.getBeacon(addr)
        beacon = MarvelmindHandler().getBeacon(addr)

        x = drone.pose.location.x
        y = drone.pose.location.y
        z = drone.pose.location.z
        rx = drone.pose.rotation.x
        ry = drone.pose.rotation.y
        rz = drone.pose.rotation.z


        if beacon is not None:
            x, y, z = beacon.x, beacon.y, beacon.z
        last_trace = Buffer().get_last_trace()
        if last_trace is not None:
            yaw, pitch, roll = last_trace.yaw, last_trace.pitch, last_trace.roll
            init_rotation = Euler((0,0,0))
            init_rotation.rotate_axis('Z', yaw)
            init_rotation.rotate_axis('X', pitch)
            init_rotation.rotate_axis('Y', roll)
            #print(init_rotation)

            rx, ry, rz = init_rotation.x, init_rotation.y, init_rotation.z

        pose = sceneModel.Pose(x, y, z, rx, ry, rz)
        DroneMovementHandler().notifyAll(pose)
    
    def modal(self, context, event):
        if event.type == "TIMER":
            
            if not PositioningSystemModalOperator.isRunning:
                self.cancel(context)
                return {'FINISHED'}
            
            DroneMovementHandler().autostop()
            
            if PositioningSystemModalOperator.isRunning:
                self._move_drone()
            
        return {'PASS_THROUGH'}

    def execute(self, context):
        # Genera drone
        # Genera Notifier y observer
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__.split(".")[0]].preferences
        dev = context.scene.prop_marvelmind_port
        #dev = addon_prefs.prop_marvelmind_port
        
        udp_clientAddr = ("192.168.0.24", 5558)
        udp_serverAddr = ("192.168.0.16", 4445)

        self._begin_thread(dev, udp_clientAddr, udp_serverAddr)
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
            # dev = addon_prefs.prop_marvelmind_port
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
