
bl_info = {
    "name": "Utilities",
    "author": "Alberto Ramos Sanchez",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "General Utilities",
    "category": "System",
    "wiki_url": "https://github.com/bertoramos/blender-editor"
}

import bpy

MODE = "DEBUG"

if MODE == "DEBUG":
    import os
    import sys
    from pathlib import Path

    project_folder = Path("E:\\Universidad\\TFM\\AplicacionBlender\\DroneAddon")
    dir = project_folder / Path(".\\utilities\\")
    if not dir in sys.path:
        sys.path.append(str(dir))

    import delete_override
    import object_properties
    import opengl_activate

    import importlib
    importlib.reload(delete_override)
    importlib.reload(object_properties)
    importlib.reload(opengl_activate)
else:
    from . import delete_override
    from . import object_properties
    from . import opengl_activate

operadores = [delete_override, opengl_activate]

paneles = []

def register():
    for op in operadores:
        op.autoregister()
    for p in paneles:
        p.autoregister()

def unregister():
    for op in operadores:
        op.autounregister()
    for p in paneles:
        p.autounregister()

if __name__=='__main__':
    register()
