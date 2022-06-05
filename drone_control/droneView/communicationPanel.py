
import bpy
from drone_control.droneController import (
                    TogglePositioningSystemOperator,
                    PositioningSystemModalOperator,
                    CalibrateOperator,
                    DropAllStaticBeacons,
                    TogglePlanOperator,
                    DroneMovementHandler,
                    ManualSimulationModalOperator,
                    ToggleCaptureOperator
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

        #if PositioningSystemModalOperator.isRunning:
        box = self.layout.box()
        box.prop(context.scene, "marvelmind_num_points", text="Num points")
        box.prop(context.scene, "marvelmind_umbral", text="Umbral")
        
        button_txt = "Stop" if DroneMovementHandler().isPlanRunning() else "Play"
        button_ico = "SNAP_FACE" if DroneMovementHandler().isPlanRunning() else "PLAY"
        self.layout.operator(TogglePlanOperator.bl_idname, text=button_txt, icon=button_ico)

        #self.layout.operator(CaptureModalOperator.bl_idname, text="Capture")
        txt_file = ("Start" if not ToggleCaptureOperator.isCapturing else "Stop") + " capture"
        self.layout.operator(ToggleCaptureOperator.bl_idname, text=txt_file)
