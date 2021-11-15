
import bpy

def draw(self, context):
    if context.window_manager.progress_status:
        self.layout.label(text=str(context.window_manager.progress_label))
        self.layout.prop(context.window_manager, "progress")

def register():
    bpy.types.WindowManager.progress_label = bpy.props.StringProperty(name="Progress title", default="Progress")

    bpy.types.WindowManager.progress = bpy.props.FloatProperty(
        name="Progress",
        subtype="PERCENTAGE",
        soft_min=0, 
        soft_max=100, 
        precision=0,
    )

    bpy.types.WindowManager.progress_status = bpy.props.BoolProperty(
        name="Progress status",
        default=False
    )

    bpy.types.VIEW3D_HT_header.append(draw)

def unregister():
    del bpy.types.WindowManager.progress
    del bpy.types.WindowManager.progress_status

    bpy.types.VIEW3D_HT_header.remove(draw)

