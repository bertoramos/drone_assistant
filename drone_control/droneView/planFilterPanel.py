
import bpy

from drone_control.droneController.droneMovementHandler import DroneMovementHandler
from drone_control.sceneModel.planCollection import PlanCollection

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
        self.layout.prop(context.scene, "plan_show_mode", text="Plan show mode")
        if context.scene.plan_show_mode == "NPOSES":
            self.layout.prop(context.scene.NPOSES_args, "nposes", text="Number poses")
