
import bpy

import drone_control.sceneModel

from drone_control import droneController


def register():
    pass

def unregister():
    pass

class DroneListPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_DroneListPanel"
    bl_label = "Drone Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone Panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row1 = layout.row()
        row1.template_list('LIST_UL_Drone', 'Drone list', scene, "drones_list", scene, "drone_list_index")
        
        row2 = layout.row()

        drone_management_ops = [(droneController.droneCreator.CreateDroneOperator.bl_idname, "PLUS"),
                                (droneController.droneCreator.RemoveDroneOperator.bl_idname, "X"),
                                (droneController.droneCreator.ModifyDroneOperator.bl_idname, "GREASEPENCIL"),
                                (droneController.droneCreator.SelectActiveDroneOperator.bl_idname, "RESTRICT_SELECT_OFF"),
                                (droneController.droneCreator.UnselectActiveDroneOperator.bl_idname, "RESTRICT_SELECT_ON")]
        
        for idname, icon in drone_management_ops:
            row2.operator(idname, icon=icon)
        row2.operator(droneController.droneCreator.LIST_OT_DroneMoveItem.bl_idname, text='', icon="TRIA_UP").direction = 'UP'
        row2.operator(droneController.droneCreator.LIST_OT_DroneMoveItem.bl_idname, text='', icon="TRIA_DOWN").direction = 'DOWN'

        layout.operator(droneController.droneCreator.DisplayDroneInfoOperator.bl_idname, text='', icon="INFO")