
from mathutils import Vector

from drone_control.patternModel.stopThread import StoppableThread
from drone_control.communication import Buffer, ConnectionHandler
from drone_control.utilsAlgorithm import MarvelmindHandler
from drone_control import sceneModel

import time

class PoseSenderThread(StoppableThread):

    def __init__(self, *args, **kwargs):
        super(PoseSenderThread, self).__init__(*args, **kwargs)
    
    def execute(self):
        from drone_control.droneController.positioningOperator import calculate_angle
        
        drone = sceneModel.DronesCollection().getActive()
        
        addr_left, addr_right = drone.address
        
        beacon_left = MarvelmindHandler().getBeacon(addr_left)
        beacon_right = MarvelmindHandler().getBeacon(addr_right)
        
        timestamp = 0
        x = drone.pose.location.x
        y = drone.pose.location.y
        z = drone.pose.location.z
        angle = drone.pose.rotation.z

        if beacon_left is not None and beacon_right is not None:
            pos_left  = Vector((beacon_left.x, beacon_left.y, beacon_left.z))
            pos_right = Vector((beacon_right.x, beacon_right.y, beacon_right.z))
            pos_mid   = (pos_left + pos_right)/2
            
            x, y, z = pos_mid.x, pos_mid.y, pos_mid.z
            res_angle = calculate_angle(beacon_left, beacon_right)
            angle = res_angle if res_angle is not None else angle
            
            timestamp = min(beacon_left.timestamp_pos, beacon_right.timestamp_pos)
        elif beacon_left is not None:
            x, y, z = beacon_left.x, beacon_left.y, beacon_left.z
            timestamp = beacon_left.timestamp_pos
        elif beacon_right is not None:
            x, y, z = beacon_right.x, beacon_right.y, beacon_right.z
            timestamp = beacon_right.timestamp_pos
        
        # now_time=int(time.time()*1000)
        # print("L=", beacon_left.timestamp_pos, " R=", beacon_right.timestamp_pos, " N=", now_time)
        # print("LD=", (beacon_left.timestamp_pos - now_time), " RD=", (beacon_right.timestamp_pos-now_time), " LRD=", (beacon_left.timestamp_pos-beacon_right.timestamp_pos))
        
        #print("SENDER POSE")
        ConnectionHandler().send_pose(timestamp, x, y, z, angle)
    
    def run(self):
        while True:
            try:
                if self.stopped():
                    break
                self.execute()
                time.sleep(0.1)
            except Exception as e:
                print(e)
