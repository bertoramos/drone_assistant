
import bpy

import drone_control.sceneModel

from drone_control import droneController
#import droneController.droneCreator.CreateDroneOperator as CreateDroneOperator
#import droneController.droneCreator.RemoveDroneOperator as RemoveDroneOperator
#import droneController.droneCreator.SelectActiveDroneOperator as SelectActiveDroneOperator
#import droneController.droneCreator.UnselectActiveDroneOperator as UnselectActiveDroneOperator

def register():
    pass

def unregister():
    pass


class DronePanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_DronePanel"
    bl_label = "Drone Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone Panel"

    def draw(self, context):
        self.layout.operator("scene.mock_possys_modal_operator")

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
                                (droneController.droneCreator.SelectActiveDroneOperator.bl_idname, "RESTRICT_SELECT_OFF"),
                                (droneController.droneCreator.UnselectActiveDroneOperator.bl_idname, "RESTRICT_SELECT_ON")]

        for idname, icon in drone_management_ops:
            row2.operator(idname, icon=icon)
        row2.operator(droneController.droneCreator.LIST_OT_DroneMoveItem.bl_idname, text='', icon="TRIA_UP").direction = 'UP'
        row2.operator(droneController.droneCreator.LIST_OT_DroneMoveItem.bl_idname, text='', icon="TRIA_DOWN").direction = 'DOWN'
