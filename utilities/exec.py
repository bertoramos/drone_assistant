
import bpy
import os
from pathlib import Path

project_folder = Path("E:\\Universidad\\TFM\\AplicacionBlender\\DroneAddon")
filename = project_folder / Path(".\\utilities\\__init__.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
