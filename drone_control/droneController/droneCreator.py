
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

def _create_drone_boxcollider(mesh_id, dimensions):
    drone_obj = bpy.data.objects[mesh_id]

    xdim, ydim, zdim = dimensions.x, dimensions.y, dimensions.z
    # Crea, posiciona y escala box collider
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0.,0.,0.), rotation=(0.,0.,0.))
    collider_obj = bpy.context.active_object
    collider_obj.name = mesh_id + "_box_collider"

    collider_obj.object_type = 'ROBOT_MARGIN'

    # Añade un material translucido
    if collider_obj.active_material is None:
        mat = bpy.data.materials.new(collider_obj.name_full + "_material")
        collider_obj.active_material = mat
        mat.diffuse_color = mathutils.Vector((0, 0, 0, 0.2))
    
    lock_object(collider_obj)

    # El box collider es hijo del mesh del drone
    # collider_obj.parent = drone_obj
    collider_obj.dimensions = mathutils.Vector((xdim, ydim, zdim))
    collider_obj.location = drone_obj.location.copy()
    collider_obj.rotation_euler = drone_obj.rotation_euler.copy()

    bpy.ops.object.select_all(action='DESELECT')
    drone_obj.select_set(True)
    collider_obj.select_set(True)
    bpy.context.view_layer.objects.active = drone_obj
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

    collider_obj.hide_select = True

    hidden = bpy.context.scene.robot_margin_hidden
    collider_obj.hide_set(hidden)
    
    return collider_obj.name_full

def _load_drone_mesh(name, start_location, start_rotation, dimension):
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    sphere_id = name
    sphere_obj = bpy.context.active_object
    sphere_obj.name = sphere_id
    sphere_id = sphere_obj.name_full
    sphere_obj.object_type = "DRONE"
    base_dim = 0.2
    xdim = 0.9 * dimension.x if dimension.x < base_dim else base_dim
    ydim = 0.9 * dimension.y if dimension.y < base_dim else base_dim
    zdim = 0.9 * dimension.z if dimension.z < base_dim else base_dim

    bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    orientation_id = name + "_orientation"
    orientation_obj = bpy.context.active_object
    orientation_obj.name = orientation_id
    orientation_id = orientation_obj.name_full
    bpy.data.objects[orientation_id].rotation_euler.y = pi/2
    bpy.data.objects[orientation_id].object_type = "DRONE_ARROW"
    bpy.data.objects[orientation_id].show_in_front = True

    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(4, 4, 4))
    axis_id = name + "_axis"
    axis_obj = bpy.context.active_object
    axis_obj.name = axis_id
    axis_id = axis_obj.name_full
    bpy.data.objects[axis_id].object_type = "DRONE_AXIS"
    bpy.data.objects[axis_id].show_in_front = True

    bpy.data.objects[orientation_id].parent = bpy.data.objects[axis_id]
    # bpy.data.objects[bearing_id].parent = bpy.data.objects[sphere_id]
    bpy.data.objects[axis_id].parent = bpy.data.objects[sphere_id]

    bpy.data.objects[sphere_id].location = start_location
    bpy.data.objects[sphere_id].rotation_euler = start_rotation
    bpy.data.objects[sphere_id].dimensions = mathutils.Vector((xdim, ydim, zdim))
    
    lock_object(bpy.data.objects[sphere_id])
    # lock_object(bpy.data.objects[bearing_id])
    lock_object(bpy.data.objects[orientation_id])
    lock_object(bpy.data.objects[axis_id])

    bpy.data.objects[orientation_id].hide_select = True
    bpy.data.objects[axis_id].hide_select = True

    axis_obj.scale = mathutils.Vector((4,4,4))
    
    return sphere_id


def _create_drone_note(mesh_id, address):
    color = mathutils.Vector((0, 0, 0, 1.0))
    font = 14
    font_align = 'C'
    hint_space = 0.1
    font_rotation = 0
    text = f"{mesh_id} | Beacon {address[0]}-{address[1]}"

    drone_note_name = draw_text(bpy.context, mesh_id + "_note", text, mathutils.Vector((0,0,0)), color, hint_space, font, font_align, font_rotation)
    if drone_note_name is not None:
        note_obj = bpy.data.objects[drone_note_name]
        lock_object(note_obj)

        bpy.data.objects[drone_note_name].parent = bpy.data.objects[mesh_id]
    return drone_note_name

def _add_drone_to_collection(name, start_location, start_rotation, dimension, address, server_addr, server_port, client_addr, client_port):
    # Load mesh
    mesh_id = _load_drone_mesh(name, start_location, start_rotation, dimension)
    collider_id = _create_drone_boxcollider(mesh_id, dimension)
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
    prop_drone_name: bpy.props.StringProperty(name="Name", description="Drone name", default="Drone", maxlen=20)
    prop_drone_location: bpy.props.FloatVectorProperty(name="Location", description="Initial drone location", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)
    prop_drone_rotation: bpy.props.FloatVectorProperty(name="Rotation", description="Initial drone rotation", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)
    prop_drone_dimension: bpy.props.FloatVectorProperty(name="Dimension", description="Dimension drone ", default=(0.5, 0.5, 0.5), min=0.0, subtype='XYZ', size=3)
    
    prop_drone_address_left: bpy.props.IntProperty(name="address_left", description="Drone address", min=1, default=13)
    prop_drone_address_right: bpy.props.IntProperty(name="address_right", description="Drone address", min=1, default=12)

    prop_drone_server_address: bpy.props.StringProperty(name="Server address", description="Server address", default="192.168.0.16")
    prop_drone_server_port: bpy.props.IntProperty(name="Server port", description="Server port", default=4445, min=1)
    prop_drone_client_address: bpy.props.StringProperty(name="Client address", description="Client address", default="0.0.0.0")
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

        address_left = context.scene.drone_props.prop_drone_address_left
        address_right = context.scene.drone_props.prop_drone_address_right
        
        address = address_left, address_right
        
        server_addr = context.scene.drone_props.prop_drone_server_address # "192.168.0.16"
        server_port = context.scene.drone_props.prop_drone_server_port # 4445
        client_addr = context.scene.drone_props.prop_drone_client_address # "192.168.0.24"
        client_port = context.scene.drone_props.prop_drone_client_port # 5558
        
        full_name = _add_drone_to_collection(name, start_location, start_rotation, dimension, address, server_addr, server_port, client_addr, client_port)
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

        row = self.layout.row()
        row.label(text="Beacon address")
        row.prop(props, "prop_drone_address_left", text="Left")
        row.prop(props, "prop_drone_address_right", text="Right")

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


class DisplayDroneInfoOperator(bpy.types.Operator):
    """Display drone info operator"""
    bl_idname = "scene.display_drone_info_operator"
    bl_label = "Drone information"
    bl_description = "Display drone information"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return len(sceneModel.DronesCollection()) > 0
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        name = context.scene.drone_props.prop_drone_name
        location = context.scene.drone_props.prop_drone_location
        rotation = context.scene.drone_props.prop_drone_rotation
        dimension = context.scene.drone_props.prop_drone_dimension

        address_left = context.scene.drone_props.prop_drone_address_left
        address_right = context.scene.drone_props.prop_drone_address_right
                
        server_addr = context.scene.drone_props.prop_drone_server_address # "192.168.0.16"
        server_port = context.scene.drone_props.prop_drone_server_port # 4445
        client_addr = context.scene.drone_props.prop_drone_client_address # "192.168.0.24"
        client_port = context.scene.drone_props.prop_drone_client_port # 5558

        self.layout.label(text=f"Name : {name}")
        
        self.layout.label(text=f"Pose:")
        
        x_txt = f"{location.x:0.3f}".rstrip('0').rstrip('.')
        y_txt = f"{location.y:0.3f}".rstrip('0').rstrip('.')
        z_txt = f"{location.z:0.3f}".rstrip('0').rstrip('.')
        rx_txt = f"{rotation.x:0.2f}".rstrip('0').rstrip('.')
        ry_txt = f"{rotation.y:0.2f}".rstrip('0').rstrip('.')
        rz_txt = f"{rotation.z:0.2f}".rstrip('0').rstrip('.')
        
        box = self.layout.box()
        row = box.row()
        row.label(text="Location <X; Y; Z>")
        row.label(text=f"<{x_txt}; {y_txt}; {z_txt}> m")
        
        row = box.row()
        row.label(text="Rotation <X; Y; Z>")
        row.label(text=f"<{rx_txt}; {ry_txt}; {rz_txt}> °")

        self.layout.label(text="Dimensions:")
        box = self.layout.box()
        row = box.row()
        row.label(text="<X;Y;Z>")

        xdim_txt = f"{location.x:0.3f}".rstrip('0').rstrip('.')
        ydim_txt = f"{location.y:0.3f}".rstrip('0').rstrip('.')
        zdim_txt = f"{location.z:0.3f}".rstrip('0').rstrip('.')

        row.label(text=f"<{xdim_txt};{ydim_txt};{zdim_txt}> m")
        
        row = self.layout.row()
        row.label(text="Beacon address")
        row.label(text=f"<{address_left};{address_right}>")
        
        row = self.layout.row()
        row.label(text="Server")
        row.label(text=f"{server_addr}:{server_port}")
        
        row = self.layout.row()
        row.label(text="Client")
        row.label(text=f"{client_addr}:{client_port}")


class ModifyDroneOperator(bpy.types.Operator):
    """Modify drone operator"""
    bl_idname = "scene.modify_drone_operator"
    bl_label = "Modify"
    bl_description = "Modify drone"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return sceneModel.PlanCollection().getActive() is None and \
               sceneModel.DronesCollection().getActive() is None and \
               len(sceneModel.DronesCollection()) > 0 and \
               not utilsAlgorithm.MarvelmindHandler().isRunning()
    
    def execute(self, context):
        drones_list = context.scene.drones_list
        drone_index = context.scene.drone_list_index

        if not 0 <= drone_index < len(drones_list):
            return {'FINISHED'}

        item = drones_list[drone_index]
        mesh_id = item.drone_name

        drone = sceneModel.DronesCollection().get(mesh_id)

        droneObj = bpy.data.objects[mesh_id]

        location = context.scene.drone_props.prop_drone_location
        rotation = context.scene.drone_props.prop_drone_rotation

        addr_left  = context.scene.drone_props.prop_drone_address_left
        addr_right = context.scene.drone_props.prop_drone_address_right

        server_addr = context.scene.drone_props.prop_drone_server_address
        server_port = context.scene.drone_props.prop_drone_server_port
        client_addr = context.scene.drone_props.prop_drone_client_address
        client_port = context.scene.drone_props.prop_drone_client_port

        drone.address       = (addr_left, addr_right)
        drone.serverAddress = server_addr
        drone.serverPort    = server_port
        drone.clientAddress = client_addr
        drone.clientPort    = client_port

        drone.translate(sceneModel.Pose(location.x, location.y, location.z, rotation.x, rotation.y, rotation.z))

        #drone_repr = str(sceneModel.DronesCollection().get(mesh_id))
        self.report({'INFO'}, f"\"{mesh_id}\" drone was modified\n")

        return {'FINISHED'}
    
    def invoke(self, context, event):
        drones_list = context.scene.drones_list
        drone_index = context.scene.drone_list_index

        if not 0 <= drone_index < len(drones_list):
            return {'FINISHED'}

        item = drones_list[drone_index]
        mesh_id = item.drone_name

        self.report({'INFO'}, f"\"{mesh_id}\" drone was selected")

        drone = sceneModel.DronesCollection().get(mesh_id)

        droneObj = bpy.data.objects[mesh_id]

        context.scene.drone_props.prop_drone_location = droneObj.location
        context.scene.drone_props.prop_drone_rotation = droneObj.rotation_euler

        context.scene.drone_props.prop_drone_address_left  = drone.address[0]
        context.scene.drone_props.prop_drone_address_right = drone.address[1]

        context.scene.drone_props.prop_drone_server_address = drone.serverAddress
        context.scene.drone_props.prop_drone_server_port    = drone.serverPort
        context.scene.drone_props.prop_drone_client_address = drone.clientAddress
        context.scene.drone_props.prop_drone_client_port    = drone.clientPort

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.drone_props

        self.layout.prop(props, "prop_drone_location", text="Location")
        self.layout.prop(props, "prop_drone_rotation", text="Rotation")

        row = self.layout.row()
        row.label(text="Beacon address")
        row.prop(props, "prop_drone_address_left", text="Left")
        row.prop(props, "prop_drone_address_right", text="Right")

        self.layout.prop(props, "prop_drone_server_address", text="Server address")
        self.layout.prop(props, "prop_drone_server_port", text="Server port")
        self.layout.prop(props, "prop_drone_client_address", text="Client address")
        self.layout.prop(props, "prop_drone_client_port", text="Client port")

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
