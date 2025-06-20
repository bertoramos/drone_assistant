
from typing import DefaultDict
import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty

import sys

DEFAULT_PORT = "COM3" if sys.platform=="win32" else "/dev/ttyACM0"

def register():
    global DEFAULT_PORT
    DEFAULT_PORT = "COM3" if sys.platform=="win32" else "/dev/ttyACM0"

    bpy.types.Scene.prop_marvelmind_port = StringProperty(
        name="Marvelmind port",
        #set=set_port,
        default=DEFAULT_PORT
    )
    
    bpy.types.Scene.prop_marvelmind_update_rate_hz = IntProperty(
        name="Marvelmind Update Rate (HZ)",
        min=1,
        default=100
    )

def unregister():
    del bpy.types.Scene.prop_marvelmind_port
    del bpy.types.Scene.prop_marvelmind_update_rate_hz

def set_port(self, value):
    import re
    port = value

    osname = sys.platform
    ospatt = re.compile("COM\d+") if osname == "win32" else re.compile("/dev/ttyACM\d+")
    
    print(osname, port, value, ospatt.match(port), ospatt)
    print(self.keys())
    if ospatt.match(port) is None:
        port = "COM3" if osname == "win32" else "/dev/ttyACM0"
        self['prop_marvelmind_port'] = port
        return
    self['prop_marvelmind_port'] = value


class DroneControlPreferences(AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "prop_marvelmind_port")
        layout.prop(context.scene, "prop_marvelmind_update_rate_hz")

