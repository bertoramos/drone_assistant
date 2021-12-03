
import bpy

def register():
    bpy.types.Scene.robot_margin_hidden = bpy.props.BoolProperty(name="robot_margin_hidden", default=False)

def unregister():
    del bpy.types.Scene.robot_margin_hidden

def hide(context):
    for obj in bpy.data.objects:
        if obj.object_type == "ROBOT_MARGIN":
            obj.hide_set(True)

def show(context):
    for obj in bpy.data.objects:
        if obj.object_type == "ROBOT_MARGIN" and obj.parent is not None and not obj.parent.hide_get():
            obj.hide_set(False)

class HideRobotMarginOperator(bpy.types.Operator):
    bl_idname = "object.hiderobotmargin"
    bl_label = "HideRobotMargin"

    #hidden = False

    @classmethod
    def poll(cls, context):
        return len([obj for obj in bpy.data.objects if obj.object_type == 'ROBOT_MARGIN']) > 0

    def execute(self, context):
        if context.scene.robot_margin_hidden:
            show(context)
            context.scene.robot_margin_hidden = False
        else:
            hide(context)
            context.scene.robot_margin_hidden = True
        return {'FINISHED'}

class HideRobotPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_HideRobot"
    bl_label = "View"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Options" # Add new tab to N-Panel

    def draw(self, context):
        txt = "Show robot margin" if context.scene.robot_margin_hidden else "Hide robot margin"
        icon = "HIDE_ON" if context.scene.robot_margin_hidden else "HIDE_OFF"
        self.layout.operator(HideRobotMarginOperator.bl_idname, text=txt, icon=icon)
