
import bpy

# begin local import: Change to from . import MODULE
# end local import: Change to from . import MODULE

items = [("TEMPORAL", "Temporal", "", -1),
         ("OTHER", "Other", "", 0),
         ("WALL", "Wall", "", 1),
         ("CEIL", "Ceil", "", 2),
         ("OBSTACLE", "Obstacle", "", 3),
         ("OBSTACLE_MARGIN", "Obstacle margin", "", 4),
         ("BLUETOOTH_BEACON", "Bluetooth_Beacon", "", 5),
         ("ULTRASOUND_BEACON", "Ultrasound_Beacon", "", 6),
         ("ROBOT", "Robot", "", 7),
         ("ROBOT_MARGIN", "Robot_margin", "", 8),
         ("ROBOT_NOTE", "Robot_note", "", 9),
         ("ROBOT_CAMERA", "Robot_camera", "", 10),
         ("PATH_ELEMENTS", "Path_elements", "", 11),
         ("GEOMETRIC_CURSOR", "Geometric_cursor", "", 12),
         ("STATIC_ULTRASOUND_BEACON", "Static_Ultrasound_Beacon", "", 13),
         ("STATIC_BLUETOOTH_BEACON", "Static_Bluetooth_Beacon", "", 14),
         ("DRONE", "Drone", "", 15),
         ("DRONE_AXIS", "Drone_axis", "", 16),
         ("DRONE_ARROW", "Drone_arrow", "", 17),
         ("DRONE_BEARING", "Drone_bearing", "", 18)]

bpy.types.Object.object_type = bpy.props.EnumProperty(items=items, default="OTHER")

# Disable change
def update_nop(self, context):
    pass

def set_nop(self, value):
    self["TOL"] = 0.001

bpy.types.Scene.TOL = bpy.props.FloatProperty(name="TOL", set=set_nop, default=0.001)
