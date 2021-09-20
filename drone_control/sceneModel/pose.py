
import bpy
import mathutils

class Pose:

    def __init__(self, x, y, z, rx, ry, rz):
        self.__location = mathutils.Vector((x, y, z))
        self.__rotation = mathutils.Euler((rx, ry, rz))

    @classmethod
    def fromVector(cls, location, rotation):
        return Pose(location.x, location.y, location.z, rotation.x, rotation.y, rotation.z)

    def __str__(self):
        return f"Pose(location={self.__location}, rotation={self.__rotation})"

    def __get_location(self):
        return self.__location

    def __get_rotation(self):
        return self.__rotation

    location = property(fget=__get_location)
    rotation = property(fget=__get_rotation)
