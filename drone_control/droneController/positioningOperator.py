
import bpy
from mathutils import Euler, Vector
import logging

from drone_control.communication import Buffer, ConnectionHandler
from drone_control import sceneModel
from .planEditor import PlanEditor
from drone_control.utilsAlgorithm import MarvelmindHandler
from .droneMovementHandler import DroneMovementHandler

from drone_control.communication import datapacket

from drone_control.utilsAlgorithm import FPSCounter

import numpy as np
import math

def calculate_angle(b1, b2):
    
    if b1 is None or b2 is None:
        return None
    if math.dist((b1.x, b1.y, b1.z), (b2.x, b2.y, b2.z)) < 1e-5:
        return None

    robot_vector = np.array([b2.x - b1.x, b2.y - b1.y])
    robot_vector = robot_vector / np.linalg.norm(robot_vector)
    x_vector = np.array([1., 0.])
    perp_vector = np.array([-1*robot_vector[1], robot_vector[0]])

    dot_product = np.dot(perp_vector, x_vector)
    angle = np.arccos(dot_product)
    
    if perp_vector[1] < 0:
        angle = 2*math.pi - angle
    
    return angle

class PositioningSystemModalOperator(bpy.types.Operator):
    bl_idname = "wm.positioning_system_modal"
    bl_label = "Positioning System Modal"

    isRunning = False
    
    _timer = None
    _observer = None
    _notifier = None
    error_message = ""

    __all_beacons = []


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
        #handler.start(device=dev, verbose=True)
        
        if not ConnectionHandler().initialize(clientAddr, serverAddr):
            print("Client socket cannot be open")
            return False
        
        ConnectionHandler().start()
        
        if not ConnectionHandler().send_change_mode(datapacket.ModePacket.CONNECT):
            self.report({"INFO"}, "Server not available")
            ConnectionHandler().stop()
            return False
        else:
            print("Mode changed to 1")
        
        handler.start(device=dev, verbose=True)

        return True

        #if not ConnectionHandler().initialize(clientAddr, serverAddr):
        #    print("Client socket cannot be open")
        #    handler.stop()
        #    return False
        #ConnectionHandler().start()
        #
        #if not ConnectionHandler().send_change_mode(1):
        #    print("Change mode not finished: Server not available")
        #    self.report({'INFO'}, 'Server not available')
        #    ConnectionHandler().stop()
        #    handler.stop()
        #    return False
        #else:
        #    print("Mode changed to 1")
        #    return True
        
        # PositioningSystemModalOperator._marvelmind_thread = MarvelmindThread(device=dev, verbose=True)
        # PositioningSystemModalOperator._marvelmind_thread.start()
    
    def _end_thread(self):
        # PositioningSystemModalOperator._marvelmind_thread.stop()
        # PositioningSystemModalOperator._marvelmind_thread.join()
        
        if not ConnectionHandler().send_change_mode(datapacket.ModePacket.DISCONNECT):
            print("Change mode not finished")
            return False
        else:
            print("Mode changed to 0")
        
        ConnectionHandler().stop()
        MarvelmindHandler().stop()
        # MarvelmindHandler().join_thread()
        
        return True
    
    def cancel(self, context):
        print("Cancel")
        self._des_observe_drone()

        return self._end_thread()

    def _move_drone(self):
        drone = sceneModel.DronesCollection().getActive()

        addr_left, addr_right = drone.address
        # beacon = PositioningSystemModalOperator._marvelmind_thread.getBeacon(addr)

        beacon_left = MarvelmindHandler().getBeacon(addr_left)
        beacon_right = MarvelmindHandler().getBeacon(addr_right)
        
        x = drone.pose.location.x
        y = drone.pose.location.y
        z = drone.pose.location.z
        rx = drone.pose.rotation.x
        ry = drone.pose.rotation.y
        rz = drone.pose.rotation.z
        
        #last_trace = Buffer().get_last_trace()
        speed = 0
        
        if beacon_left is not None and beacon_right is not None:
            pos_left  = Vector((beacon_left.x, beacon_left.y, beacon_left.z))
            pos_right = Vector((beacon_right.x, beacon_right.y, beacon_right.z))
            pos_mid   = (pos_left + pos_right)/2
            
            x, y, z = pos_mid.x, pos_mid.y, pos_mid.z
            angle = calculate_angle(beacon_left, beacon_right)
            if angle is not None:
                rx, ry, rz = 0, 0, angle
        elif beacon_left is not None:
            x, y, z = beacon_left.x, beacon_left.y, beacon_left.z
            self.__all_beacons.append(beacon_left)
            speed = beacon_left.speed
        elif beacon_right is not None:
            x, y, z = beacon_right.x, beacon_right.y, beacon_right.z
            self.__all_beacons.append(beacon_right)
            speed = beacon_right.speed
        
        #if last_trace is not None:
        #    yaw, pitch, roll = last_trace.yaw, last_trace.pitch, last_trace.roll
        #    init_rotation = Euler((0,0,0))
        #    init_rotation.rotate_axis('Z', yaw)
        #    init_rotation.rotate_axis('X', pitch)
        #    init_rotation.rotate_axis('Y', roll)
        #    #print(init_rotation)
        #
        #    rx, ry, rz = init_rotation.x, init_rotation.y, init_rotation.z
        
        pose = sceneModel.Pose(x, y, z, rx, ry, rz)
        DroneMovementHandler().notifyAll(pose, speed)
        FPSCounter().notifyRender()
    
    def modal(self, context, event):
        if event.type == "TIMER":
            if not PositioningSystemModalOperator.isRunning:
                res = self.cancel(context)
                return {'FINISHED'}
            
            DroneMovementHandler().autostop()
            
            if PositioningSystemModalOperator.isRunning:
                self._move_drone()
            
        return {'PASS_THROUGH'}

    def execute(self, context):
        # Genera drone
        # Genera Notifier y observer
        PositioningSystemModalOperator.isRunning = True

        preferences = context.preferences
        addon_prefs = preferences.addons[__name__.split(".")[0]].preferences
        dev = context.scene.prop_marvelmind_port
        #dev = addon_prefs.prop_marvelmind_port

        drone = sceneModel.DronesCollection().getActive()
        
        #udp_clientAddr = ("192.168.0.24", 5558)
        #udp_serverAddr = ("192.168.0.16", 4445)
        udp_clientAddr = (drone.clientAddress, drone.clientPort)
        udp_serverAddr = (drone.serverAddress, drone.serverPort)
        
        if not self._begin_thread(dev, udp_clientAddr, udp_serverAddr):
            PositioningSystemModalOperator.isRunning = False
            return {'FINISHED'}
        self._observe_drone()
        
        wm = context.window_manager
        wm.modal_handler_add(self)
        self._timer = wm.event_timer_add(0.1, window=context.window)
        
        PositioningSystemModalOperator.error_message = ""

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
