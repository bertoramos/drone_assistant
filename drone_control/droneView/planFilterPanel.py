
import bpy

from drone_control.droneController.droneMovementHandler import DroneMovementHandler
from drone_control.sceneModel.planCollection import PlanCollection

def show_full_plan():
    pass

def show_current_level():
    pass


class ShowFullPlanOperator(bpy.types.Operator):
    bl_idname = "object.showfullplan"
    bl_label = "Show Full Plan"

    @classmethod
    def poll(cls, context):
        return DroneMovementHandler().isPlanRunning()

    def execute(self, context):
        return {'FINISHED'}


class FilterNextPosesOperator(bpy.types.Operator):
    bl_idname = "object.show_n_poses"
    bl_label = "Show N poses"
    
    number_poses: bpy.props.IntProperty(name="Number poses", min=1, default=2)

    @classmethod
    def poll(cls, context):
        return DroneMovementHandler().isPlanRunning()
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        print(self.number_poses)
        PlanExecutionToolsPanel.current_mode = FilterNextPosesOperator.bl_idname
        return {'FINISHED'}

class FilterByLevelOperator(bpy.types.Operator):
    bl_idname = "object.filter_by_level"
    bl_label = "Show current level"

    @classmethod
    def poll(cls, context):
        return DroneMovementHandler().isPlanRunning()
    
    def execute(self, context):
        PlanExecutionToolsPanel.current_mode = FilterByLevelOperator.bl_idname
        return {'FINISHED'}


class PlanExecutionToolsPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_PlanExecutionToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS" 
    bl_context = "objectmode"
    bl_label = "Execution Tools"

    current_mode = None

    @classmethod
    def poll(cls, context):
        return DroneMovementHandler().isPlanRunning()
    
    def draw(self, context):
        box = self.layout.box()
        box.label(text="Filter")
        select_icon = "RESTRICT_SELECT_OFF"

        self.layout.operator(FilterNextPosesOperator.bl_idname, icon=select_icon if PlanExecutionToolsPanel.current_mode == FilterNextPosesOperator.bl_idname else "NONE")

