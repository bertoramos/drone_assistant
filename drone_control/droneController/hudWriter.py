
import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader

from dataclasses import dataclass
from typing import List

@dataclass
class RGBAColor:
    red  : float
    green: float
    blue : float
    alpha: float
    
    def __post_init__(self):
        assert 0 <= self.red   <= 1, "Red channel is a float between 0 and 1"
        assert 0 <= self.green <= 1, "Green channel is a float between 0 and 1"
        assert 0 <= self.blue  <= 1, "Blue channel is a float between 0 and 1"
        assert 0 <= self.alpha <= 1, "Alpha channel is a float between 0 and 1"

@dataclass
class Texto:
    font_id: int = 0
    x: float = 15
    y: float = 30

    size: int = 20
    dpi : int = 72

    text_color: RGBAColor = RGBAColor(0,0,0,1)

    text: str = "TEXTO"

@dataclass
class Point2D:
    x: float
    y: float

@dataclass
class Point3D:
    x: float
    y: float
    z: float

@dataclass
class Curve:
    points : List
    color : RGBAColor = RGBAColor(0,0,0,1)


def __draw_curve_3d(points, color):
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": points})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)

def draw_callback_px(self, context):
    font_id = 0
    # Draw text 2D
    for k in HUDWriterOperator._textos:
        txt = HUDWriterOperator._textos[k]
        
        blf.position(txt.font_id, txt.x, txt.y, 0)
        blf.size(txt.font_id, txt.size, txt.dpi)
        blf.color(txt.font_id, txt.text_color.red, txt.text_color.green, txt.text_color.blue, txt.text_color.alpha)
        blf.draw(txt.font_id, txt.text)

def draw_view_callback_px(self, context):
    
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    # bgl.glEnable(bgl.GL_DEPTH_TEST)
    
    for k in HUDWriterOperator._curves_3d:
        curve = HUDWriterOperator._curves_3d[k]

        points = []
        for p in curve.points:
            if type(p) == Point3D:
                xi, yi, zi = p.x, p.y, p.z
                points.append((xi, yi, zi))
        color = (curve.color.red, curve.color.green, curve.color.blue, curve.color.alpha)

        __draw_curve_3d(points, color)
    
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_LINE_SMOOTH)
    # bgl.glEnable(bgl.GL_DEPTH_TEST)

class HUDWriterOperator(bpy.types.Operator):
    bl_idname = "wm.hudwriter"
    bl_label = "HUDWriter"
    
    _open = False
    _textos = {}
    _curves_3d = {}

    def redraw(self, context):
        context.area.tag_redraw()
        for screen in bpy.context.workspace.screens:
            for area in screen.areas:
                area.tag_redraw()

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

    def modal(self, context, event):
        if event.type == 'TIMER':
            self.redraw(context)
        
        if not HUDWriterOperator._open:
            bpy.types.SpaceView3D.draw_handler_remove(self._handler_2d, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self._handler_3d, 'WINDOW')
            self.redraw(context)
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)

            self._handler_2d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            self._handler_3d = bpy.types.SpaceView3D.draw_handler_add(draw_view_callback_px, args, 'WINDOW', 'POST_VIEW')

            self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
            
            context.window_manager.modal_handler_add(self)

            HUDWriterOperator._open = True

            return {'RUNNING_MODAL'}
        
        else:
            self.report({'WARNING'}, 'View3D not found')


class ShowHUDOperator(bpy.types.Operator):
    bl_idname = "wm.showhud"
    bl_label = "ShowHUD"

    def execute(self, context):
        if not HUDWriterOperator._open:
            bpy.ops.wm.hudwriter('INVOKE_DEFAULT')
        else:
            HUDWriterOperator._open = False
        return {'FINISHED'}

class ShowHUDPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_ShowHUD"
    bl_label = "View"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Options" # Add new tab to N-Panel

    def draw(self, context):
        txt = "Hide HUD information" if HUDWriterOperator._open else "Show HUD information"
        icon = "HIDE_ON" if HUDWriterOperator._open else "HIDE_OFF"
        self.layout.operator(ShowHUDOperator.bl_idname, text=txt, icon=icon)
