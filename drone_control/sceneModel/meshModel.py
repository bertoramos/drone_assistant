
import bpy
from abc import ABC
from copy import deepcopy
from mathutils import Vector, Euler

from .pose import Pose

class MeshModel(ABC):

    def __init__(self, meshID: str, pose: Pose, colliderID: str = None, noteID: str = None):
        self.__pose = pose
        self.__meshID = meshID
        self.__colliderID = colliderID
        self.__noteID = noteID

    def translate(self, pose: Pose):
        self.__pose = pose
        if self.__meshID in bpy.data.objects:
            bpy.data.objects[self.__meshID].location = self.__pose.location
            bpy.data.objects[self.__meshID].rotation_euler = self.__pose.rotation
        else:
            import warnings
            warnings.warn(f"'{self.__meshID}' object not found in current scene", RuntimeWarning)

    def __str__(self):
        return f"MeshModel({self.__meshID}) = {self.__pose}"

    def __del__(self):
        print("Deleted")
        if self.__meshID in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[self.__meshID], do_unlink=True)
        if self.__colliderID is not None:
            bpy.data.objects.remove(bpy.data.objects[self.__colliderID], do_unlink=True)
        if self.__noteID is not None:
            bpy.data.objects.remove(bpy.data.objects[self.__noteID], do_unlink=True)


    def __get_pose(self):
        return deepcopy(self.__pose)

    def __get_meshID(self):
        return self.__meshID

    def __get_colliderID(self):
        return self.__colliderID

    pose = property(fget=__get_pose)
    meshID = property(fget=__get_meshID)
    colliderID = property(fget=__get_colliderID)
