
import bpy
from bpy.types import Operator, SpaceView3D
from mathutils import Vector

# measureit execute method AddNote operator
# Antonio Vazquez
def draw_text(context, name, text, loc, color, hint_space, font, font_align, font_rotation):
    """
    - context: blender context
    - text: str
        display text
    - loc: Vector
        3D location
    - color: Vector
        rgb color (0, 1)
    - hint_space: int
    """
    if context.area.type == 'VIEW_3D':
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        myempty = bpy.data.objects[bpy.context.active_object.name]
        myempty.location = loc
        myempty.empty_display_size = 0.01
        myempty.name = name

        scene = context.scene
        mainobject = myempty
        if 'MeasureGenerator' not in mainobject:
            mainobject.MeasureGenerator.add()
        mp = mainobject.MeasureGenerator[0]

        for cont in range(len(mp.measureit_segments)-1, mp.measureit_num):
            mp.measureit_segments.add()

        ms = mp.measureit_segments[mp.measureit_num]
        ms.gltype = 10
        ms.glpointa = 0
        ms.glpointb = 0
        ms.glcolor = color # Vector(0,0,0,0)
        ms.glspace = hint_space # (-100, 100) def=0.1

        ms.gltxt = text # str
        ms.glfont_size = font # int
        ms.glfont_align = font_align # 'L', 'C', 'R' EnumProperty
        ms.glfont_rotat = font_rotation # 0-360

        mp.measureit_num += 1

        context.area.tag_redraw()
        return myempty.name
    return None
