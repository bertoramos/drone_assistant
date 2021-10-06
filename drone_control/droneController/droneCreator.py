
import bpy
from math import pi, radians
import mathutils
import bpy_extras

import logging

from drone_control import sceneModel
from drone_control.utilsAlgorithm import draw_text
from .planEditor import PlanEditor
from . import manualSimulationControl
from drone_control import utilsAlgorithm

def register():
    bpy.types.Scene.drones_list = bpy.props.CollectionProperty(type=DroneListItem)
    bpy.types.Scene.drone_list_index = bpy.props.IntProperty(name="Index for drone_list_index", default=0)

    bpy.types.Scene.drone_props = bpy.props.PointerProperty(type=DroneProps)

def unregister():
    del bpy.types.Scene.drones_list
    del bpy.types.Scene.drone_list_index
    del bpy.types.Scene.drone_props

##############################################################################

def _toRadians(rotation):
    x = radians(rotation.x)
    y = radians(rotation.y)
    z = radians(rotation.z)

    return mathutils.Vector((x,y,z))

def lock_object(obj):
    obj.protected = True
    obj.lock_location[0:3] = (True, True, True)
    obj.lock_rotation[0:3] = (True, True, True)
    obj.lock_scale[0:3] = (True, True, True)

def _create_drone_boxcollider(mesh_id, collider_proportion):
    drone_obj = bpy.data.objects[mesh_id]

    xdim, ydim, zdim = drone_obj.dimensions.x, drone_obj.dimensions.y, drone_obj.dimensions.z
    xperc, yperc, zperc = collider_proportion.x, collider_proportion.y, collider_proportion.z

    # Crea, posiciona y escala box collider
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0.,0.,0.), rotation=(0.,0.,0.))
    collider_obj = bpy.context.active_object
    collider_obj.name = mesh_id + "_box_collider"
    collider_obj.dimensions = mathutils.Vector((xdim + (xdim*xperc/100), ydim + (ydim*yperc/100), zdim + (zdim*zperc/100)))

    collider_obj.object_type = 'ROBOT_MARGIN'

    # Añade un material translucido
    if collider_obj.active_material is None:
        mat = bpy.data.materials.new(collider_obj.name_full + "_material")
        collider_obj.active_material = mat
        mat.diffuse_color = mathutils.Vector((0, 0, 0, 0.2))

    lock_object(collider_obj)

    # El box collider es hijo del mesh del drone
    collider_obj.parent = drone_obj

    return collider_obj.name_full

def _load_drone_mesh(name, start_location, start_rotation, dimension):
    bpy.ops.mesh.primitive_cone_add(radius1=1,
                                    radius2=0,
                                    depth=2,
                                    end_fill_type='NGON', calc_uvs=True, enter_editmode=False, align='WORLD',
                                    location=(0, 0, 0),
                                    rotation=(-pi/2, 0, 0),
                                    scale=(1, 0.5, 1))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # nombre dado por el usuario
    bpy.context.active_object.name = name
    mesh_id = bpy.context.active_object.name_full

    drone_obj = bpy.data.objects[mesh_id]
    drone_obj.location = start_location
    drone_obj.rotation_euler = start_rotation
    drone_obj.dimensions = dimension

    drone_obj.object_type = "DRONE"

    lock_object(drone_obj)

    return mesh_id

def _create_drone_note(mesh_id, address):
    color = mathutils.Vector((1.0, 1.0, 1.0, 1.0))
    font = 14
    font_align = 'C'
    hint_space = 0.1
    font_rotation = 0
    text = f"{mesh_id} | Beacon {address}"

    drone_note_name = draw_text(bpy.context, mesh_id + "_note", text, mathutils.Vector((0,0,0)), color, hint_space, font, font_align, font_rotation)
    if drone_note_name is not None:
        note_obj = bpy.data.objects[drone_note_name]
        lock_object(note_obj)

        bpy.data.objects[drone_note_name].parent = bpy.data.objects[mesh_id]
    return drone_note_name

def _add_drone_to_collection(name, start_location, start_rotation, dimension, collider_proportion, address, server_addr, server_port, client_addr, client_port):

    # Load mesh
    mesh_id = _load_drone_mesh(name, start_location, start_rotation, dimension)
    collider_id = _create_drone_boxcollider(mesh_id, collider_proportion)
    note_id = _create_drone_note(mesh_id, address)
    drone_obj = bpy.data.objects[mesh_id]

    # Create model
    pose = sceneModel.pose.Pose(drone_obj.location.x,
                                drone_obj.location.y,
                                drone_obj.location.z,
                                drone_obj.rotation_euler.x,
                                drone_obj.rotation_euler.y,
                                drone_obj.rotation_euler.z)
    
    drone = sceneModel.droneModel.DroneModel(mesh_id, pose, collider_id, note_id, address, server_addr, server_port, client_addr, client_port)

    sceneModel.dronesCollection.DronesCollection().add(drone)

    return mesh_id

################################################################################

class DroneListItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""

    drone_name: bpy.props.StringProperty(
           name="Name",
           description="Drone name",
           default="Untitled")

class LIST_UL_Drone(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        name = item.drone_name
        active_drone = sceneModel.dronesCollection.DronesCollection().getActive()
        active_name = None if active_drone is None else active_drone.meshID
        custom_icon = 'PINNED' if active_name == name else 'UNPINNED'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=name, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class DroneProps(bpy.types.PropertyGroup):
    prop_drone_name: bpy.props.StringProperty(name="Name", description="Drone name",default="Drone", maxlen=20)
    prop_drone_location: bpy.props.FloatVectorProperty(name="Location", description="Initial drone location", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)
    prop_drone_rotation: bpy.props.FloatVectorProperty(name="Rotation", description="Initial drone rotation", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)
    prop_drone_dimension: bpy.props.FloatVectorProperty(name="Dimension", description="Dimension drone ", default=(2.0, 2.0, 1.0), min=0.0, subtype='XYZ', size=3)
    prop_drone_collider_proportion: bpy.props.FloatVectorProperty(name="Margin percentage", description="Drone margin percentage", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3, min=0.0, max=100.0)
    prop_drone_address: bpy.props.IntProperty(name="address", description="Drone address", min=1, default=6)
    prop_drone_server_address: bpy.props.StringProperty(name="Server address", description="Server address", default="192.168.0.16")
    prop_drone_server_port: bpy.props.IntProperty(name="Server port", description="Server port", default=4445, min=1)
    prop_drone_client_address: bpy.props.StringProperty(name="Client address", description="Client address", default="192.168.0.24")
    prop_drone_client_port: bpy.props.IntProperty(name="Client port", description="Client port", default=5558, min=1)

class CreateDroneOperator(bpy.types.Operator):
    """Creates a drone"""
    bl_idname = "scene.create_drone_operator"
    bl_label = "Create"
    bl_description = "Create drone"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        name = context.scene.drone_props.prop_drone_name
        start_location = context.scene.drone_props.prop_drone_location
        start_rotation = _toRadians(context.scene.drone_props.prop_drone_rotation)
        dimension = context.scene.drone_props.prop_drone_dimension
        collider_proportion = context.scene.drone_props.prop_drone_collider_proportion
        address = context.scene.drone_props.prop_drone_address
        server_addr = context.scene.drone_props.prop_drone_server_address # "192.168.0.16"
        server_port = context.scene.drone_props.prop_drone_server_port # 4445
        client_addr = context.scene.drone_props.prop_drone_client_address # "192.168.0.24"
        client_port = context.scene.drone_props.prop_drone_client_port # 5558
        
        full_name = _add_drone_to_collection(name, start_location, start_rotation, dimension, collider_proportion, address, server_addr, server_port, client_addr, client_port)
        item = context.scene.drones_list.add()
        item.drone_name = full_name

        logger = logging.getLogger("myblenderlog")
        logger.info(f"A drone model named \"{full_name}\" was created")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.drone_props
        self.layout.prop(props, "prop_drone_name", text="Name")
        self.layout.prop(props, "prop_drone_location", text="Location")
        self.layout.prop(props, "prop_drone_rotation", text="Rotation")
        self.layout.prop(props, "prop_drone_dimension", text="Dimension")
        self.layout.prop(props, "prop_drone_collider_proportion", text="Margin proportion")
        self.layout.prop(props, "prop_drone_address", text="Address")
        self.layout.prop(props, "prop_drone_server_address", text="Server address")
        self.layout.prop(props, "prop_drone_server_port", text="Server port")
        self.layout.prop(props, "prop_drone_client_address", text="Client address")
        self.layout.prop(props, "prop_drone_client_port", text="Client port")

class RemoveDroneOperator(bpy.types.Operator):
    """Remove active drone"""
    bl_idname = "scene.remove_drone_operator"
    bl_label = "Remove"
    bl_description = "Remove drone"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if manualSimulationControl.ManualSimulationModalOperator.isRunning:
            return False

        drones_list = context.scene.drones_list
        drone_index = context.scene.drone_list_index

        if not 0 <= drone_index < len(drones_list):
            return False

        item = drones_list[drone_index]
        mesh_id = item.drone_name

        activeDrone = sceneModel.dronesCollection.DronesCollection().getActive()

        isActive = activeDrone.meshID == mesh_id if activeDrone is not None else False

        count = 0
        for plan in sceneModel.planCollection.PlanCollection():
            if plan.droneID == item.drone_name:
                count += 1

        inAnyPlan = count > 0

        editorActive = PlanEditor().isActive

        len_drone_list = len(context.scene.drones_list) > 0

        return len_drone_list and \
               not isActive and \
               not inAnyPlan and \
               not editorActive and \
               not utilsAlgorithm.MarvelmindHandler().isRunning()

    def execute(self, context):
        # Busca elemento
        drones_list = context.scene.drones_list
        drone_index = context.scene.drone_list_index

        if not 0 <= drone_index < len(drones_list):
            return {'FINISHED'}

        item = drones_list[drone_index]
        mesh_id = item.drone_name

        count = 0
        for plan in sceneModel.planCollection.PlanCollection():
            if plan.droneID == item.drone_name:
                count += 1

        if count > 0:
            self.report({'ERROR'}, f"{item.drone_name} cannot be deleted because it is associated with " + ( f"{count} plans" if count > 1 else "a plan" ))
            return {'FINISHED'}

        # Elimina de coleccion
        drone = sceneModel.dronesCollection.DronesCollection().get(mesh_id)
        sceneModel.dronesCollection.DronesCollection().remove(mesh_id)
        del drone

        # Elimina de la lista
        drones_list.remove(drone_index)
        context.scene.drone_list_index = min(max(0, drone_index - 1), len(drones_list) - 1)

        logger = logging.getLogger("myblenderlog")
        logger.info(f"A drone model named \"{mesh_id}\" was eliminated")

        return {'FINISHED'}

class SelectActiveDroneOperator(bpy.types.Operator):
    """Select active drone"""
    bl_idname = "scene.select_active_drone_operator"
    bl_label = "Select"
    bl_description = "Select drone"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.scene.drones_list) > 0 and \
                context.scene.drone_list_index >= 0 and \
                not manualSimulationControl.ManualSimulationModalOperator.isRunning and \
                sceneModel.PlanCollection().getActive() is None and \
                not utilsAlgorithm.MarvelmindHandler().isRunning()

    def execute(self, context):
        drones_list = context.scene.drones_list
        drone_index = context.scene.drone_list_index

        if not 0 <= drone_index < len(drones_list):
            return {'FINISHED'}

        item = drones_list[drone_index]
        mesh_id = item.drone_name

        sceneModel.dronesCollection.DronesCollection().setActive(mesh_id)

        logger = logging.getLogger("myblenderlog")
        logger.info(f"\"{mesh_id}\" drone was selected")

        return {'FINISHED'}

class UnselectActiveDroneOperator(bpy.types.Operator):
    """Select active drone"""
    bl_idname = "scene.unselect_active_drone_operator"
    bl_label = "Unselect"
    bl_description = "Unselect drone"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if manualSimulationControl.ManualSimulationModalOperator.isRunning:
            return False

        drones_list = context.scene.drones_list
        drone_index = context.scene.drone_list_index

        if not 0 <= drone_index < len(drones_list):
            return False

        item = drones_list[drone_index]
        item_meshid = item.drone_name

        if sceneModel.dronesCollection.DronesCollection().getActive() is None:
            return False

        drone_meshid = sceneModel.dronesCollection.DronesCollection().getActive().meshID

        isActiveSelected = item_meshid == drone_meshid

        noPlanActive = sceneModel.PlanCollection().getActive() is None

        return noPlanActive and \
               len(context.scene.drones_list) > 0 and \
               isActiveSelected and \
               not utilsAlgorithm.MarvelmindHandler().isRunning()

    def execute(self, context):
        sceneModel.dronesCollection.DronesCollection().unsetActive()
        return {'FINISHED'}

class LIST_OT_DroneMoveItem(bpy.types.Operator):
    """Move an item in the list."""

    bl_idname = "drones_list.move_item"
    bl_label = "Move an item in the list"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', "")))

    @classmethod
    def poll(cls, context):
        return len(context.scene.drones_list) > 1

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.scene.drone_list_index
        list_length = len(bpy.context.scene.drones_list) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.scene.drone_list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        drones_list = context.scene.drones_list
        index = context.scene.drone_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        drones_list.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}
