
import bpy

from drone_control import droneController


def register():
    pass


def unregister():
    pass


class EditorPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_EditorPanel"
    bl_label = "Editor Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone Panel"

    def draw(self, context):
        self.layout.template_list("LIST_UL_PlanList", "Plan list", context.scene,
                                    "plan_list", context.scene, "plan_list_index")

        row = self.layout.row()
        row.operator(droneController.planCreator.CreatePlanEditorOperator.bl_idname, icon="PLUS")
        row.operator(droneController.planCreator.ModifyPlanEditorOperator.bl_idname, icon="GREASEPENCIL")
        row.operator(droneController.planCreator.RemovePlanEditorOperator.bl_idname, icon="X")

        row = self.layout.row()
        row.operator(droneController.planCreator.ActivePlanOperator.bl_idname, icon="RESTRICT_SELECT_OFF")
        row.operator(droneController.planCreator.DesactivePlanOperator.bl_idname, icon="RESTRICT_SELECT_ON")

        self.layout.operator(droneController.planCreator.TemporalShowPlanOperator.bl_idname)

class EditorToolsPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_EditorToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Plan editor tools"

    @classmethod
    def poll(cls, context):
        return droneController.planEditor.PlanEditor().isActive

    def draw(self, context):
        box = self.layout.box()
        box.label(text="Plan information")
        box.label(text="Plan ID : " + droneController.planEditor.PlanEditor().currentPlanID)
        box.label(text="Drone ID : " + droneController.planEditor.PlanEditor().currentDroneID)

        editor_ops = [(droneController.planCreator.AddPoseOperator.bl_idname, "PLUS"),
                      (droneController.planCreator.RemovePoseOperator.bl_idname, "X"),
                      (droneController.planCreator.InsertPoseBeforeOperator.bl_idname, "NODE_INSERT_OFF")]

        for idname, icon in editor_ops:
            self.layout.operator(idname, icon=icon)

        editor_ops = [(droneController.planCreator.SavePlanEditorOperator.bl_idname, "DISK_DRIVE"),
                      (droneController.planCreator.DiscardPlanOperator.bl_idname, "REMOVE")]

        row = self.layout.row()
        for idname, icon in editor_ops:
            row.operator(idname, icon=icon)
