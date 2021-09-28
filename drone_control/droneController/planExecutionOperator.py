
import bpy

from .droneMovementHandler import DroneMovementHandler
from drone_control.sceneModel import PlanCollection

class TogglePlanOperator(bpy.types.Operator):
    bl_idname = "scene.toggleplan"
    bl_label = "TogglePlan"

    @classmethod
    def poll(cls, context):
        return DroneMovementHandler().isPositioningRunning() and \
               PlanCollection().getActive() is not None

    def execute(self, context):
        if not DroneMovementHandler().isPlanRunning():
            DroneMovementHandler().start_plan()
        else:
            DroneMovementHandler().stop_plan()
        return {'FINISHED'}
