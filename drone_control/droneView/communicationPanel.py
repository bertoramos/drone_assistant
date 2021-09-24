
import bpy
from drone_control.droneController import (
                    TogglePositioningSystemOperator,
                    PositioningSystemModalOperator,
                    CalibrateOperator,
                    DropAllStaticBeacons
)

class CommunicationPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_CommunicationPanel"
    bl_label = "Communication Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone Panel"

    def draw(self, context):
        button_txt = "Connect" if not PositioningSystemModalOperator.isRunning else "Disconnect"
        button_ico = "RESTRICT_INSTANCED_ON" if not PositioningSystemModalOperator.isRunning else "RESTRICT_INSTANCED_OFF"
        self.layout.operator(TogglePositioningSystemOperator.bl_idname, text=button_txt, icon=button_ico)
        self.layout.operator(CalibrateOperator.bl_idname)
        self.layout.operator(DropAllStaticBeacons.bl_idname)