
import bpy
import mathutils
import math

from itertools import chain

def register():
    bpy.types.Scene.bg_z_img = bpy.props.StringProperty(name="bg_z_color", default="")
    bpy.types.Scene.bg_x_img = bpy.props.StringProperty(name="bg_x_color", default="")
    bpy.types.Scene.bg_y_img = bpy.props.StringProperty(name="bg_y_color", default="")

    #create_lateral(bpy.context, bpy.context.scene.lat_color)
    #create_top(bpy.context, bpy.context.scene.top_color)

    bpy.types.Scene.top_color = bpy.props.FloatVectorProperty(name="Top color", description="Top color", subtype="COLOR", size=4, min=0.0, max=1.0, default=(1.0, 1.0, 1.0, 1.0), update=update_top)
    bpy.types.Scene.lat_color = bpy.props.FloatVectorProperty(name="Lateral color", description="Lateral color", subtype="COLOR", size=4, min=0.0, max=1.0, default=(1.0, 1.0, 1.0, 1.0), update=update_lateral)


def unregister():
    del bpy.types.Scene.bg_z_img
    del bpy.types.Scene.bg_x_img
    del bpy.types.Scene.bg_y_img

    del bpy.types.Scene.top_color
    del bpy.types.Scene.lat_color


def update_lateral(self, context):
    # get_lateral(context, context.scene.lat_color)
    if context.scene.bg_x_img == "" and context.scene.bg_y_img == "":
        create_lateral(context, context.scene.lat_color)
    else:
        get_lateral(context,  context.scene.lat_color)

def update_top(self, context):
    # get_top(context, context.scene.top_color)
    if context.scene.bg_z_img == "":
        create_top(context, context.scene.top_color)
    else:
        get_top(context, context.scene.top_color)


def generateUniformColor(width, height, color):
    for y in range(height):
        for x in range(width):
            # Generate a color for the pixel at (x, y).
            # This is the OpenGL coordinate system, so (0, 0) is the bottom-left corner of the image
            # and (WIDTH, HEIGHT) is the top-right corner of the image.
            yield color

def create_lateral(context, bg_color):
    width = 100
    height = 100
    color = tuple(bg_color[:])
    img_data = bpy.data.images.new(name="TOP_BG_IMG", width=width, height=height)

    img_data.pixels = tuple(chain.from_iterable(generateUniformColor(width, height, color)))
    img_data.update()
    
    #img = bpy.data.images[]
    bpy.ops.object.empty_add(type='IMAGE', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    img_x_axis = bpy.context.active_object

    bpy.ops.object.empty_add(type='IMAGE', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    img_y_axis = bpy.context.active_object

    img_x_axis.rotation_euler = mathutils.Euler((math.radians(90), 0, 0))
    img_y_axis.rotation_euler = mathutils.Euler((0, math.radians(90), 0))

    img_x_axis.data = img_data
    img_y_axis.data = img_data
    
    img_x_axis.empty_image_depth = "BACK"
    img_x_axis.empty_image_side = "DOUBLE_SIDED"
    img_x_axis.show_in_front = False
    img_x_axis.show_empty_image_orthographic = True
    img_x_axis.show_empty_image_perspective = True
    img_x_axis.show_empty_image_only_axis_aligned = True

    img_y_axis.empty_image_depth = "BACK"
    img_y_axis.empty_image_side = "DOUBLE_SIDED"
    img_y_axis.show_in_front = False
    img_y_axis.show_empty_image_orthographic = True
    img_y_axis.show_empty_image_perspective = True
    img_y_axis.show_empty_image_only_axis_aligned = True
    
    img_x_axis.scale = mathutils.Vector((15_000, 15_000, 15_000))
    img_y_axis.scale = mathutils.Vector((15_000, 15_000, 15_000))

    img_x_axis.lock_location[:] = (True, True, True)
    img_x_axis.lock_rotation[:] = (True, True, True)
    img_x_axis.lock_scale[:] = (True, True, True)
    img_x_axis.hide_select = True

    img_y_axis.lock_location[:] = (True, True, True)
    img_y_axis.lock_rotation[:] = (True, True, True)
    img_y_axis.lock_scale[:] = (True, True, True)
    img_y_axis.hide_select = True

    context.scene.bg_x_img = img_x_axis.name_full
    context.scene.bg_y_img = img_y_axis.name_full

def create_top(context, bg_color):
    width = 100
    height = 100
    color = tuple(bg_color[:])
    img_data = bpy.data.images.new(name="TOP_BG_IMG", width=width, height=height)

    img_data.pixels = tuple(chain.from_iterable(generateUniformColor(width, height, color)))
    img_data.update()
    
    #img = bpy.data.images[]
    bpy.ops.object.empty_add(type='IMAGE', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    img_empty = bpy.context.active_object

    img_empty.data = img_data

    img_empty.empty_image_depth = "BACK"
    img_empty.empty_image_side = "DOUBLE_SIDED"
    img_empty.show_in_front = False
    img_empty.show_empty_image_orthographic = True
    img_empty.show_empty_image_perspective = True
    img_empty.show_empty_image_only_axis_aligned = True
    
    img_empty.scale = mathutils.Vector((15_000, 15_000, 15_000))

    img_empty.lock_location[:] = (True, True, True)
    img_empty.lock_rotation[:] = (True, True, True)
    img_empty.lock_scale[:] = (True, True, True)
    img_empty.hide_select = True

    context.scene.bg_z_img = img_empty.name_full


def get_lateral(context, bg_color):
    width = 100
    height = 100
    color = tuple(bg_color[:])

    img_x_axis = bpy.data.objects[context.scene.bg_x_img]
    img_y_axis = bpy.data.objects[context.scene.bg_y_img]
    
    img_x_data = img_x_axis.data
    img_y_data = img_y_axis.data

    img_x_data.pixels = tuple(chain.from_iterable(generateUniformColor(width, height, color)))
    img_x_data.update()

    img_y_data.pixels = tuple(chain.from_iterable(generateUniformColor(width, height, color)))
    img_y_data.update()

def get_top(context, bg_color):
    width = 100
    height = 100
    color = tuple(bg_color[:])

    img_z_axis = bpy.data.objects[context.scene.bg_z_img]
    img_data = img_z_axis.data
    
    img_data.pixels = tuple(chain.from_iterable(generateUniformColor(width, height, color)))
    img_data.update()

class ColoringPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_ColoringPanel"
    bl_label = "Background color"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Options"

    def draw(self, context):
        self.layout.prop(context.scene, "top_color")
        self.layout.prop(context.scene, "lat_color")

