
import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader

from dataclasses import dataclass
from typing import List, Callable
from bpy_types import Context

from mathutils import Vector

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
    text: Callable[[Context], str] = lambda context: "TEXTO"
    font_id: int = 0
    x: Callable[[Context], int] = 15
    y: Callable[[Context], int] = 30

    size: Callable[[Context], int] = 20
    dpi : int = 72

    text_color: RGBAColor = RGBAColor(0,0,0,1)

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
    color  : RGBAColor = RGBAColor(0, 0, 0, 1)

@dataclass
class DashedCurve:
    points : List
    scale  : float
    color  : RGBAColor = RGBAColor(0, 0, 0, 1)

@dataclass
class Arrow:
    start: Point3D
    end: Point3D
    head_len: float
    head_size: float
    color  : RGBAColor = RGBAColor(0, 0, 0, 1)

@dataclass
class Star:
    point: Point3D
    size: float

    color: RGBAColor = RGBAColor(1, 1, 0, 1)

#######################################################

def get_fixed_perpendicular(u):

    v1 = Vector((u.y, -u.x,    0))
    v2 = Vector((u.z,    0, -u.x))
    v3 = Vector((  0,  u.z, -u.y))

    if v1.length > 0:
        return v1
    elif v2.length > 0:
        return v2
    elif v3.length > 0:
        return v3
    return None


def __draw_arrow_3d(arrow):
    # color, start, end, head_length, head_size
    start = Vector((arrow.start.x, arrow.start.y, arrow.start.z))
    end = Vector((arrow.end.x, arrow.end.y, arrow.end.z))
    head_length = arrow.head_len
    head_size = arrow.head_size
    color = arrow.color.red, arrow.color.green, arrow.color.blue, arrow.color.alpha
    
    start_vec = Vector(start)
    end_vec = Vector(end)

    u = (end_vec-start_vec).normalized()
    
    # Arrow line
    __draw_line_3d(color, start, end)
    
    v = get_fixed_perpendicular(u).normalized()
    w = u.cross(v)

    vi = -v
    wi = -w

    corner_a = end_vec-head_size*v
    corner_b = end_vec-head_size*w
    corner_c = end_vec-head_size*vi
    corner_d = end_vec-head_size*wi

    peak = end_vec + head_length*u

    __draw_line_3d(color, corner_a, peak)
    __draw_line_3d(color, corner_b, peak)
    __draw_line_3d(color, corner_c, peak)
    __draw_line_3d(color, corner_d, peak)
    
    # draw_line_3d((0,1,0,1), end_vec, end_vec-head_size*v)
    # draw_line_3d((0,1,0,1), end_vec, end_vec-head_size*w)
    # draw_line_3d((0,1,0,1), end_vec, end_vec-head_size*vi)
    # draw_line_3d((0,1,0,1), end_vec, end_vec-head_size*wi)
    
    for i, p_a in enumerate([corner_a, corner_b, corner_c, corner_d]):
        for j, p_b in enumerate([corner_a, corner_b, corner_c, corner_d]):
            if i > j: __draw_line_3d(color, p_a, p_b)

def __draw_line_3d(color, start, end):
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": [start,end]})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)

def __draw_curve_3d(curve):
    points = [(p.x, p.y, p.z) for p in curve.points]
    color = (curve.color.red, curve.color.green, curve.color.blue, curve.color.alpha)

    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": points})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)

def __draw_dotted_curve_3d(curve):
    # Reutilizado de https://docs.blender.org/api/current/gpu.html#custom-shader-for-dotted-3d-line
    
    vertex_shader = '''
    uniform mat4 u_ViewProjectionMatrix;

    in vec3 position;
    in float arcLength;

    out float v_ArcLength;

    void main()
    {
        v_ArcLength = arcLength;
        gl_Position = u_ViewProjectionMatrix * vec4(position, 1.0f);
    }
    '''

    fragment_shader = '''
        uniform float u_Scale;
        uniform vec4 u_color;

        in float v_ArcLength;
        out vec4 FragColor;

        void main()
        {
            if (step(sin(v_ArcLength * u_Scale), 0.5) == 1) discard;
            FragColor = u_color; // vec4(1.0);
        }
    '''

    color = [curve.color.red, curve.color.green, curve.color.blue, curve.color.alpha]
    coords = [Vector((p.x, p.y, p.z)) for p in curve.points]
    arc_lengths = [0]
    for a, b in zip(coords[:-1], coords[1:]):
        arc_lengths.append(arc_lengths[-1] + (a - b).length)
    
    shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
    batch = batch_for_shader(
        shader, 'LINE_STRIP',
        {"position": coords, "arcLength": arc_lengths},
    )

    shader.bind()
    matrix = bpy.context.region_data.perspective_matrix
    shader.uniform_float("u_ViewProjectionMatrix", matrix)
    shader.uniform_float("u_Scale", curve.scale)
    shader.uniform_float("u_color", color)
    batch.draw(shader)

def __draw_star(star):
    size = star.size / 2
    pos = Vector((star.point.x, star.point.y, star.point.z))
    color = star.color

    curves = [0]*5
    curves[0] = Curve([Point3D(pos.x - size, pos.y, pos.z), Point3D(pos.x + size, pos.y, pos.z)], color)
    curves[1] = Curve([Point3D(pos.x, pos.y - size, pos.z), Point3D(pos.x, pos.y + size, pos.z)], color)
    curves[2] = Curve([Point3D(pos.x, pos.y, pos.z - size), Point3D(pos.x, pos.y, pos.z + size)], color)

    curves[3] = Curve([Point3D(pos.x - size, pos.y - size, pos.z), Point3D(pos.x + size, pos.y + size, pos.z)], color)
    curves[4] = Curve([Point3D(pos.x - size, pos.y + size, pos.z), Point3D(pos.x + size, pos.y - size, pos.z)], color)

    for c in curves:
        __draw_curve_3d(c)

############################################################################

def draw_callback_px(self, context):
    font_id = 0
    # Draw text 2D
    for k in HUDWriterOperator._textos:
        txt = HUDWriterOperator._textos[k]
        
        blf.position(txt.font_id, txt.x(context), txt.y(context), 0)
        blf.size(txt.font_id, txt.size, txt.dpi)
        blf.color(txt.font_id, txt.text_color.red, txt.text_color.green, txt.text_color.blue, txt.text_color.alpha)
        blf.draw(txt.font_id, txt.text(context))


def draw_view_callback_px(self, context):
    
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    # bgl.glEnable(bgl.GL_DEPTH_TEST)
    
    for k in HUDWriterOperator._curves_3d:
        curve = HUDWriterOperator._curves_3d[k]
        __draw_curve_3d(curve)
        #points = []
        #for p in curve.points:
        #    if type(p) == Point3D:
        #        xi, yi, zi = p.x, p.y, p.z
        #        points.append((xi, yi, zi))
        #color = (curve.color.red, curve.color.green, curve.color.blue, curve.color.alpha)
    
    for k in HUDWriterOperator._arrows_3d:
        arrow = HUDWriterOperator._arrows_3d[k]
        __draw_arrow_3d(arrow)
    
    for k in HUDWriterOperator._star_3d:
        star = HUDWriterOperator._star_3d[k]
        __draw_star(star)
    
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_LINE_SMOOTH)
    # bgl.glEnable(bgl.GL_DEPTH_TEST)

    for k in HUDWriterOperator._dashed_curve_3d:
        curve = HUDWriterOperator._dashed_curve_3d[k]
        __draw_dotted_curve_3d(curve)


def default_hud_create(context):

    def persp(text_context):
        r3d = text_context.space_data.region_3d
        view_persp = r3d.view_perspective

        if view_persp == "PERSP":
            return "PERSPECTIVE"
        else:
            TOP    = Vector((0, 0, -1))
            BOTTOM = Vector((0, 0, 1))
            LEFT   = Vector((1, 0, 0))
            RIGHT  = Vector((-1, 0, 0))
            FRONT  = Vector((0, 1, 0))
            BACK   = Vector((0, -1, 0))

            view_rotation = r3d.view_rotation.to_euler()
            vp = Vector((0,0,-1))
            vp.rotate(view_rotation)

            if (TOP - vp).length < 0.001:
                return "TOP"
            if (BOTTOM - vp).length < 0.001:
                return "BOTTOM"
            if (LEFT - vp).length < 0.001:
                return "LEFT"
            if (RIGHT - vp).length < 0.001:
                return "RIGHT"
            if (FRONT - vp).length < 0.001:
                return "FRONT"
            if (BACK - vp).length < 0.001:
                return "BACK"
    
    x = lambda pos_context: pos_context.area.width // 2 - 20
    y = lambda pos_context: pos_context.area.height - 50
    print(x(context), y(context))
    txt = Texto()
    txt.text = persp
    txt.x = x
    txt.y = y
    HUDWriterOperator._textos['VIEW_TYPE'] = txt

def default_hud_delete(context):
    if 'VIEW_TYPE' in HUDWriterOperator._textos:
        del HUDWriterOperator._textos['VIEW_TYPE']

class HUDWriterOperator(bpy.types.Operator):
    bl_idname = "wm.hudwriter"
    bl_label = "HUDWriter"
    
    _open = False
    _textos = {}
    _curves_3d = {}
    _dashed_curve_3d = {}
    _arrows_3d = {}
    _star_3d = {}

    def redraw(self, context):
        #context.area.tag_redraw()
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

            default_hud_delete(context)
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)

            self._handler_2d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            self._handler_3d = bpy.types.SpaceView3D.draw_handler_add(draw_view_callback_px, args, 'WINDOW', 'POST_VIEW')

            self._timer = context.window_manager.event_timer_add(0.1, window=context.window)

            default_hud_create(context)
            
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
