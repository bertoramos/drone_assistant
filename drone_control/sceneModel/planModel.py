
import bpy
import math
import mathutils

from .pose import Pose
from drone_control.utilsAlgorithm import draw_text
from .dronesCollection import DronesCollection

def remove_cursor(name):
    obj = bpy.data.objects[name]
    for child in obj.children:
        bpy.data.objects.remove(child)
    bpy.data.objects.remove(obj)

def create_cursor(location, rotation, dim, margin_dim, margin_scale, position_num):
    bpy.ops.mesh.primitive_cone_add(radius1=1,
                                    radius2=0,
                                    depth=2,
                                    end_fill_type='NGON', calc_uvs=True, enter_editmode=False, align='WORLD',
                                    location=(0, 0, 0),
                                    rotation=(-math.pi/2, 0, 0),
                                    scale=(1, 0.5, 1))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # nombre dado por el usuario
    bpy.context.active_object.name = "Cursor"
    cursor_name = bpy.context.active_object.name_full

    cursor_obj = bpy.data.objects[cursor_name]
    cursor_obj.location = location
    cursor_obj.rotation_euler = rotation
    cursor_obj.dimensions = dim
    cursor_obj.protected = True

    cursor_obj.object_type = "PATH_ELEMENTS"

    bpy.ops.mesh.primitive_cube_add(enter_editmode=False,
                                    align='WORLD',
                                    location=(0, 0, 0),
                                    scale=(1, 1, 1))

    # Collider obj
    collider_obj = bpy.context.active_object
    collider_obj.lock_location[0:3] = (True, True, True)
    collider_obj.lock_rotation[0:3] = (True, True, True)
    collider_obj.lock_scale[0:3] = (True, True, True)
    collider_obj.dimensions = margin_dim
    collider_obj.scale = margin_scale

    collider_obj.parent = cursor_obj

    collider_obj.object_type = 'ROBOT_MARGIN'

    collider_obj.hide_select = True

    # Añade un material translucido
    if collider_obj.active_material is None:
        mat = bpy.data.materials.new(collider_obj.name_full + "_material")
        collider_obj.active_material = mat
        mat.diffuse_color = mathutils.Vector((0, 0, 0, 0.2))

    # Dibuja anotacion
    color = mathutils.Vector((1.0, 1.0, 1.0, 1.0))
    font = 14
    font_align = 'C'
    hint_space = 0.1
    font_rotation = 0
    text = f"{position_num}"

    position_note_name = draw_text(bpy.context, "Note_pose", text, mathutils.Vector((0,0,0)), color, hint_space, font, font_align, font_rotation)
    if position_note_name is not None:
        note_obj = bpy.data.objects[position_note_name]
        note_obj.protected = True
        note_obj.lock_location[0:3] = (True, True, True)
        note_obj.lock_rotation[0:3] = (True, True, True)
        note_obj.lock_scale[0:3] = (True, True, True)

        note_obj.parent = cursor_obj

    if cursor_obj.active_material is None:
        mat = bpy.data.materials.new(cursor_obj.name_full + "_material")
        cursor_obj.active_material = mat
        mat.diffuse_color = mathutils.Vector((1.0, 1.0, 1.0, 0.6))

    return cursor_name


class PlanModel:

    def __init__(self, planID, droneID):
        self.__planID = planID
        self.__droneID = droneID
        self.__plan = []

        self.__plan_meshes = []

    def addPose(self, pose: Pose):
        self.__plan.append(pose)

    def removePose(self, poseIndex: int):
        if poseIndex in self.__plan:
            del self.__plan[poseIndex]

    def getPose(self, poseIndex: int):
        if poseIndex in self.__plan:
            return self.__plan[poseIndex]
        return None

    def setPose(self, poseIndex: int, newPose: Pose):
        if poseIndex in self.__plan:
            self.__plan[poseIndex] = newPose

    def draw(self):
        drone = DronesCollection().get(self.__droneID)
        drone_obj = bpy.data.objects[drone.meshID] if drone.meshID in bpy.data.objects else None
        collider_obj = bpy.data.objects[drone.colliderID] if drone.colliderID in bpy.data.objects else None

        if drone_obj is None or collider_obj is None: return

        for position_num, pose in enumerate(self.__plan):
            cursor_name = create_cursor(pose.location, pose.rotation, drone_obj.dimensions.copy(), collider_obj.dimensions.copy(), collider_obj.scale.copy(), position_num)

            self.__plan_meshes.append(cursor_name)

            bpy.data.objects[cursor_name].lock_location[:] = (True, True, True)
            bpy.data.objects[cursor_name].lock_rotation[:] = (True, True, True)
            bpy.data.objects[cursor_name].lock_scale[:] = (True, True, True)

    def delete(self):
        for name in self.__plan_meshes:
            remove_cursor(name)
        self.__plan_meshes.clear()

    def __iter__(self):
        return iter(self.__plan)

    def __get_planID(self):
        return self.__planID

    def __get_droneID(self):
        return self.__droneID

    planID = property(fget=__get_planID)
    droneID = property(fget=__get_droneID)
