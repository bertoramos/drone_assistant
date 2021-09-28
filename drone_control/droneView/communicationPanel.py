
import bpy
from drone_control.droneController import (
                    TogglePositioningSystemOperator,
                    PositioningSystemModalOperator,
                    CalibrateOperator,
                    DropAllStaticBeacons,
                    TogglePlanOperator,
                    DroneMovementHandler,
                    ManualSimulationModalOperator
                    
)

class CommunicationPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_CommunicationPanel"
    bl_label = "Communication Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone Panel"

    def draw(self, context):
        self.layout.operator(ManualSimulationModalOperator.bl_idname)

        button_txt = "Connect" if not PositioningSystemModalOperator.isRunning else "Disconnect"
        button_ico = "RESTRICT_INSTANCED_ON" if not PositioningSystemModalOperator.isRunning else "RESTRICT_INSTANCED_OFF"
        self.layout.operator(TogglePositioningSystemOperator.bl_idname, text=button_txt, icon=button_ico)
        self.layout.operator(CalibrateOperator.bl_idname)
        self.layout.operator(DropAllStaticBeacons.bl_idname)
        
        button_txt = "Stop" if DroneMovementHandler().isPlanRunning() else "Play"
        button_ico = "SNAP_FACE" if DroneMovementHandler().isPlanRunning() else "PLAY"
        self.layout.operator(TogglePlanOperator.bl_idname, text=button_txt, icon=button_ico)
