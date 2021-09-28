
from typing import DefaultDict
import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty

import sys

DEFAULT_PORT = "COM4" if sys.platform=="win32" else "/dev/ttyACM0"

def register():
    global DEFAULT_PORT
    DEFAULT_PORT = "COM4" if sys.platform=="win32" else "/dev/ttyACM0"

def unregister():
    pass

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
        set=set_port,
        default=DEFAULT_PORT
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "prop_marvelmind_port")

