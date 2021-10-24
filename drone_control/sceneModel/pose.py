
import bpy
import mathutils
import math

class Pose:

    def __init__(self, x, y, z, rx, ry, rz):
        self.__location = mathutils.Vector((x, y, z))
        self.__rotation = mathutils.Euler((rx, ry, rz))

    @classmethod
    def fromVector(cls, location, rotation):
        return Pose(location.x, location.y, location.z, rotation.x, rotation.y, rotation.z)
    
    def get_location_distance(self, pose):
        return ( self.__location - pose.location ).length
    
    def get_rotation_distance(self, pose):
        #self_vec = self.__rotation.to_matrix()
        #pose_vec = pose.rotation.to_matrix()

        #R = self_vec @ pose_vec.transposed()
        #trace_R = R[0][0] + R[1][1] + R[2][2]

        #angle = math.acos( (trace_R - 1)/2 )
        #return angle
        rot0 = self.__rotation.to_quaternion()
        rot1 = pose.rotation.to_quaternion()

        dif = rot0.rotation_difference(rot1)
        euler_dif = dif.to_euler()
        return euler_dif
    
    def __str__(self):
        return f"Pose(location={self.__location}, rotation={self.__rotation})"
    
    def __get_location(self):
        return self.__location

    def __get_rotation(self):
        return self.__rotation

    location = property(fget=__get_location)
    rotation = property(fget=__get_rotation)
