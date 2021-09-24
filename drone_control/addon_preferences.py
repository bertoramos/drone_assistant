
import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty

import sys

def update_port(self, context):
    pass

def get_port(self):
    return self["prop_marvelmind_port"]

def set_port(self, value):
    import re
    port = value

    osname = sys.platform
    ospatt = re.compile("COM\d+") if osname == "win32" else re.compile("/dev/tty\w+")
    
    if ospatt.match(port) is None:
        port = "COM4" if osname == "win32" else "/dev/ttyACM0"
    
    self['prop_marvelmind_port'] = port


class DroneControlPreferences(AddonPreferences):
    bl_idname = __package__
    
    prop_marvelmind_port: StringProperty(
        name="Marvelmind port",
        update=update_port,
        get=get_port,
        set=set_port,
        default="COM4" if sys.platform=="win32" else "/dev/ttyACM0"
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "prop_marvelmind_port")

