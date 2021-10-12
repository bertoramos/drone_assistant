
import bpy
from abc import ABC
from copy import deepcopy
from mathutils import Vector, Euler

from .pose import Pose


def drop(obj):
    obj_name = obj.name
    mesh = obj.data
    material = obj.active_material

    # Eliminamos objeto
    if obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)

    # Eliminamos el mesh que lo forma
    if mesh is not None:
        mesh_name = mesh.name
        if mesh_name in bpy.data.meshes:
            bpy.data.meshes.remove(bpy.data.meshes[mesh_name], do_unlink=True)
        if mesh_name in bpy.data.lights:
            bpy.data.lights.remove(bpy.data.lights[mesh_name], do_unlink=True)

    # Eliminamos su material
    if material is not None:
        material_name = material.name
        if material_name in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials[material_name], do_unlink=True)
    # bpy.ops.select_all
    bpy.ops.object.select_all(action='DESELECT')


def get_children(parent):
    not_visited = [parent]
    children = []
    while len(not_visited) > 0:
        current_node = not_visited.pop(0)
        children.extend(current_node.children)
        not_visited.extend(current_node.children)
    return children


def delete(to_delete_obj):
    protected_obj = []
    to_delete = [to_delete_obj] # map deleted objects : avoid an invalid object error when the child of a selected object is also selected
    for obj in to_delete:
        children = get_children(obj)
        for child in children:
            if child in to_delete: # indicates selected child was deleted
                to_delete.remove(child)
            drop(child)
    drop(obj)



class MeshModel(ABC):

    def __init__(self, meshID: str, pose: Pose, colliderID: str = None, noteID: str = None):
        self.__pose = pose
        self.__meshID = meshID
        self.__colliderID = colliderID
        self.__noteID = noteID

    def translate(self, pose: Pose):
        self.__pose = pose

    def __str__(self):
        return f"MeshModel({self.__meshID}) = {self.__pose}"
    
    def __del__(self):
        print("Deleted")
        delete(bpy.data.objects[self.__meshID])
        #for obj in bpy.data.objects[self.__meshID].children:
        #    bpy.data.objects.remove(bpy.data.objects[obj.name_full], do_unlink=True)
        #if self.__meshID in bpy.data.objects:
        #    bpy.data.objects.remove(bpy.data.objects[self.__meshID], do_unlink=True)
        #if self.__colliderID is not None:
        #    bpy.data.objects.remove(bpy.data.objects[self.__colliderID], do_unlink=True)
        #if self.__noteID is not None:
        #    bpy.data.objects.remove(bpy.data.objects[self.__noteID], do_unlink=True)
    
    def __get_pose(self):
        return deepcopy(self.__pose)

    def __get_meshID(self):
        return self.__meshID

    def __get_colliderID(self):
        return self.__colliderID

    pose = property(fget=__get_pose)
    meshID = property(fget=__get_meshID)
    colliderID = property(fget=__get_colliderID)
