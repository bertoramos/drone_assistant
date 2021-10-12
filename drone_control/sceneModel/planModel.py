
import bpy
import math
import mathutils

from .pose import Pose
from drone_control.utilsAlgorithm import draw_text
from .dronesCollection import DronesCollection


def lock_object(obj):
    obj.protected = True
    obj.lock_location[0:3] = (True, True, True)
    obj.lock_rotation[0:3] = (True, True, True)
    obj.lock_scale[0:3] = (True, True, True)


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


def remove_cursor(to_delete_obj):
    protected_obj = []
    to_delete = [to_delete_obj] # map deleted objects : avoid an invalid object error when the child of a selected object is also selected
    for obj in to_delete:
        children = get_children(obj)
        for child in children:
            if child in to_delete: # indicates selected child was deleted
                to_delete.remove(child)
            drop(child)
    drop(obj)

def create_cursor(location, rotation, dim, margin_dim, margin_scale, position_num):
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(0.2, 0.2, 0.2))
    sphere_id = "Cursor"
    sphere_obj = bpy.context.active_object
    sphere_obj.name = sphere_id
    sphere_id = sphere_obj.name_full
    sphere_obj.dimensions = dim
    sphere_obj.object_type = "PATH_ELEMENTS"

    bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    orientation_id = "Cursor_orientation"
    orientation_obj = bpy.context.active_object
    orientation_obj.name = orientation_id
    orientation_id = orientation_obj.name_full
    bpy.data.objects[orientation_id].rotation_euler.x = -math.pi/2
    bpy.data.objects[orientation_id].object_type = "DRONE_ARROW"
    bpy.data.objects[orientation_id].show_in_front = True

    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    axis_id = "Cursor_axis"
    axis_obj = bpy.context.active_object
    axis_obj.name = axis_id
    axis_id = axis_obj.name_full
    bpy.data.objects[axis_id].object_type = "DRONE_AXIS"
    bpy.data.objects[axis_id].show_in_front = True

    bpy.data.objects[orientation_id].hide_select = True
    bpy.data.objects[axis_id].hide_select = True

    bpy.data.objects[orientation_id].parent = bpy.data.objects[axis_id]
    bpy.data.objects[axis_id].parent = bpy.data.objects[sphere_id]

    bpy.data.objects[sphere_id].location = location
    bpy.data.objects[axis_id].rotation_euler = rotation


    bpy.ops.mesh.primitive_cube_add(enter_editmode=False,
                                    align='WORLD',
                                    location=(0, 0, 0),
                                    scale=(1, 1, 1))

    # Collider obj
    collider_obj = bpy.context.active_object
    collider_obj.lock_location[0:3] = (True, True, True)
    collider_obj.lock_rotation[0:3] = (True, True, True)
    collider_obj.lock_scale[0:3] = (True, True, True)
    collider_obj.location = sphere_obj.location
    collider_obj.dimensions = margin_dim
    collider_obj.scale = margin_scale

    #collider_obj.parent = sphere_obj
    bpy.ops.object.select_all(action='DESELECT')
    sphere_obj.select_set(True)
    collider_obj.select_set(True)
    bpy.context.view_layer.objects.active = sphere_obj
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

    collider_obj.object_type = 'ROBOT_MARGIN'

    collider_obj.hide_select = True

    # Añade un material translucido
    if collider_obj.active_material is None:
        mat = bpy.data.materials.new(collider_obj.name_full + "_material")
        collider_obj.active_material = mat
        mat.diffuse_color = mathutils.Vector((0, 0, 0, 0.2))

    # lock_object(bpy.data.objects[sphere_id])
    # lock_object(bpy.data.objects[bearing_id])
    lock_object(bpy.data.objects[orientation_id])
    lock_object(bpy.data.objects[axis_id])
    lock_object(bpy.data.objects[collider_obj.name_full])

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

        note_obj.parent = sphere_obj

    if sphere_obj.active_material is None:
        mat = bpy.data.materials.new(sphere_obj.name_full + "_material")
        sphere_obj.active_material = mat
        mat.diffuse_color = mathutils.Vector((1.0, 1.0, 1.0, 0.6))

    return sphere_id

"""
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
"""

class PlanModel:

    def __init__(self, planID, droneID):
        self.__planID = planID
        self.__droneID = droneID
        self.__plan = []

        self.__plan_meshes = []

        self.__original_color = dict({})
        self.__highlight_color = (0., 1., 0., 1.)

    def addPose(self, pose: Pose):
        self.__plan.append(pose)

    def removePose(self, poseIndex: int):
        if 0 <= poseIndex < len(self.__plan):
            del self.__plan[poseIndex]

    def getPose(self, poseIndex: int):
        if 0 <= poseIndex < len(self.__plan):
            return self.__plan[poseIndex]
        return None

    def setPose(self, poseIndex: int, newPose: Pose):
        if 0 <= poseIndex < len(self.__plan):
            self.__plan[poseIndex] = newPose
    
    def highlight(self, poseIndex: int):
        self.no_highlight()
        obj = bpy.data.objects[self.__plan_meshes[poseIndex]]
        self.__change_color(obj)
    
    def no_highlight(self):
        for obj_name in self.__plan_meshes:
            obj = bpy.data.objects[obj_name]
            self.__set_original_color(obj)
    
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
            remove_cursor(bpy.data.objects[name])
        self.__plan_meshes.clear()

    def __iter__(self):
        return iter(self.__plan)

    def __get_planID(self):
        return self.__planID

    def __get_droneID(self):
        return self.__droneID

    planID = property(fget=__get_planID)
    droneID = property(fget=__get_droneID)

    ### VIEW

    def __change_color(self, obj):
        mat = obj.active_material
        if mat is None:
            mat = bpy.data.materials.new(obj.name_full + "_mat")
            obj.active_material = mat
        if obj.name_full not in self.__original_color:
            self.__original_color[obj.name_full] = mat.diffuse_color[:]
        mat.diffuse_color = self.__highlight_color
    
    def __set_original_color(self, obj):
        mat = obj.active_material
        if mat is None:
            return
        if obj.name_full not in self.__original_color:
            return
        mat.diffuse_color = self.__original_color[obj.name_full]
