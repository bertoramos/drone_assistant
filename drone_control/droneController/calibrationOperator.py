
import bpy
from mathutils import Vector, Euler
import time

from drone_control.utilsAlgorithm import draw_text
from .positioningOperator import PositioningSystemModalOperator
from drone_control.utilsAlgorithm import MarvelmindHandler

def register():
    bpy.types.Scene.static_beacon_props = bpy.props.PointerProperty(type=StaticBeaconProps)
    bpy.types.Scene.static_ultrasound_beacon_props = bpy.props.PointerProperty(type=StaticUltrasoundBeaconProps)

def unregister():
    del bpy.types.Scene.static_beacon_props
    del bpy.types.Scene.static_ultrasound_beacon_props

beacon_types = [#("BLUETOOTH", "Bluetooth", "", 1),
                ("ULTRASOUND", "Ultrasound", "", 2)]

class StaticBeaconProps(bpy.types.PropertyGroup):
    # Propiedades comunes
    prop_beacon_name: bpy.props.StringProperty(name="Name", description="Beacon name",default="Beacon", maxlen=20)
    prop_position: bpy.props.FloatVectorProperty(name="Position", description="Beacon position", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)
    prop_type_beacon: bpy.props.EnumProperty(items = beacon_types)

#class StaticBluetoothBeaconProps(bpy.types.PropertyGroup):
#    prop_rotation: bpy.props.FloatVectorProperty(name="Rotation", description="Beacon rotation", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)


#def create_bluetooth_beacon(self, context):
#    pass

def draw_beacon_note(context, loc, text, color, font, font_align):
    # Draw notes
    name = "Beacon_note"
    hint_space = 10
    rotation = 0
    beacon_note = draw_text(context, name, text, loc, color, hint_space, font, font_align, rotation)

    bpy.data.objects[beacon_note].lock_location[0:3] = (True, True, True)
    bpy.data.objects[beacon_note].lock_rotation[0:3] = (True, True, True)
    bpy.data.objects[beacon_note].lock_scale[0:3] = (True, True, True)
    bpy.data.objects[beacon_note].protected = True

    bpy.data.objects[beacon_note].object_type = "ROBOT_NOTE"

    return beacon_note


class StaticUltrasoundBeaconProps(bpy.types.PropertyGroup):
    prop_rotation: bpy.props.FloatVectorProperty(name="Rotation", description="Beacon rotation", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)


def create_ultrasound_beacon(self, context, beacon_id):
    beacon_props = bpy.context.scene.static_beacon_props
    name = beacon_props.prop_beacon_name
    loc = beacon_props.prop_position.xyz

    ultrasound_beacon_props = bpy.context.scene.static_ultrasound_beacon_props
    
    bpy.ops.object.light_add(type='SUN', location=(loc.x, loc.y, loc.z))

    beacon = bpy.context.object
    beacon.object_type = "STATIC_ULTRASOUND_BEACON"
    beacon.name = name

    beacon.rotation_euler = ultrasound_beacon_props.prop_rotation

    beacon.protected = True
    
    # Eliminar las siguientes lineas en caso que se quiera que los beacon sean modificables por el usuario
    beacon.hide_select = True
    beacon.lock_location[:] = (True, True, True)
    beacon.lock_rotation[:] = (True, True, True)
    beacon.lock_scale[:] = (True, True, True)
    beacon.lock_rotation_w = True
    beacon.lock_rotations_4d = True

    # Crea anotacion
    loc = Vector((0,0,0))
    text = f"ID {beacon_id}  =>  " + \
           f"(x; y; z) = ({beacon.location.x:0.2f}; {beacon.location.y:0.2f}; {beacon.location.z:0.2f})"
    color = Vector((255,0,0,255))
    font = 14
    font_align = "L"

    beacon_note = draw_beacon_note(context, loc, text, color, font, font_align)
    note = bpy.data.objects[beacon_note]
    # Asigna como child de beacon

    note.parent = beacon


beacon_create_function = {#"BLUETOOTH" : [create_bluetooth_beacon],
                            "ULTRASOUND": [create_ultrasound_beacon]}

def create_static_beacon(self, context, beacon_type, beacon_id):
    beacon_create_function.get(beacon_type, lambda self, context: self.report({'ERROR'}, beacon_type + ' does not exist'))[0](self, context, beacon_id)


def delete(obj):
    for child in bpy.data.objects[obj.name].children:
        bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(bpy.data.objects[obj.name], do_unlink=True)


def drop_all_static_beacons():
    for obj in bpy.data.objects:
        if obj.object_type in DropAllStaticBeacons.static_beacons:
            delete(obj)


class DropAllStaticBeacons(bpy.types.Operator):
    bl_idname = "wm.drop_all_static_beacons"
    bl_label = "Drop all static beacons"
    bl_description = "Drop all static beacons"

    static_beacons = {"STATIC_ULTRASOUND_BEACON", "STATIC_BLUETOOTH_BEACON"}

    @classmethod
    def poll(cls, context):
        return any([o.object_type in DropAllStaticBeacons.static_beacons for o in bpy.data.objects]) and \
               PositioningSystemModalOperator.isRunning

    def execute(self, context):
        drop_all_static_beacons()
        return {'FINISHED'}


class CalibrateOperator(bpy.types.Operator):
    bl_idname = "wm.calibrate"
    bl_label = "Calibrate"
    bl_description = "Synchronize scenarios drawing static beacons"

    prop_type_beacon: bpy.props.EnumProperty(items = beacon_types)

    @classmethod
    def poll(cls, context):
        return PositioningSystemModalOperator.isRunning

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "prop_type_beacon", text="Type beacon")

    def execute(self, context):
        beacon_type = self.prop_type_beacon

        drop_all_static_beacons()

        # data = cnh.ConnectionHandler().receive_calibration_data()
        start_time = time.time()
        wait_time = 10

        stationary_beacons = MarvelmindHandler().getStationaryBeacons()
        while len(stationary_beacons) == 0 and abs(start_time - time.time()) < wait_time:
            stationary_beacons = MarvelmindHandler().getStationaryBeacons()

        if stationary_beacons is None:
            self.report({'ERROR'}, "Calibration process could not be started")
            return {'FINISHED'}
        
        for d in stationary_beacons:
            context.scene.static_beacon_props.prop_beacon_name = "Beacon {}".format(d.address)
            context.scene.static_beacon_props.prop_position = Vector((d.x, d.y, d.z))
            context.scene.static_beacon_props.prop_type_beacon = beacon_type

            if beacon_type == "ULTRASOUND":
                context.scene.static_ultrasound_beacon_props.prop_rotation = Euler((0, 0, 0))
            create_static_beacon(self, context, beacon_type, d.address)

        return {'FINISHED'}
