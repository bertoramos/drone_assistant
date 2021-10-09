
import bpy
import logging

from drone_control import sceneModel

from .planEditor import PlanEditor
from .planValidator import PlanValidatorOperator
from . import manualSimulationControl
from drone_control import utilsAlgorithm

def register():
    bpy.types.Scene.plan_list = bpy.props.CollectionProperty(type = PlanListItem)
    bpy.types.Scene.plan_list_index = bpy.props.IntProperty(name = "Index for plan_list", default = 0)

def unregister():
    del bpy.types.Scene.plan_list_index
    del bpy.types.Scene.plan_list

################################################################################

class PlanListItem(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(
           name="Name",
           description="Plan name",
           default="Untitled")

    drone_name: bpy.props.StringProperty(
        name="Drone",
        description="Drone name",
        default="Untitled"
    )

class LIST_UL_PlanList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        active_plan = sceneModel.PlanCollection().getActive()
        active_plan_name = active_plan.planID if active_plan is not None else ""
        custom_icon = "PINNED" if active_plan_name == item.name else "UNPINNED"

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = custom_icon)
            layout.label(text=item.drone_name)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)
            layout.label(text=item.drone_name)



################################################################################

class CreatePlanEditorOperator(bpy.types.Operator):
    bl_idname = "wm.create_plan_editor"
    bl_label = "Create"
    bl_description = "Create plan"

    def drone_list_callback(self, context):
        return ( (drone[1].meshID, drone[1].meshID, "") for drone in sceneModel.DronesCollection() )

    new_plan_name : bpy.props.StringProperty(name="Plan name")
    drone_name : bpy.props.EnumProperty(
        items=drone_list_callback,
        name="Drone",
        description="Choose a drone",
        default=None,
        options={'ANIMATABLE'},
        update=None,
        get=None,
        set=None
    )

    def draw(self, context):
        self.layout.prop(self, "new_plan_name")
        self.layout.prop(self, "drone_name")
    
    @classmethod
    def poll(cls, context):
        return not PlanEditor().isActive and \
               sceneModel.PlanCollection().getActive() is None and \
               len(sceneModel.DronesCollection()) > 0

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if self.new_plan_name in sceneModel.PlanCollection():
            self.report({'ERROR'}, f"{self.new_plan_name} already exists")

            logger = logging.getLogger("myblenderlog")
            logger.info(f"Given plan name is in use")

            return {'FINISHED'}

        if self.new_plan_name == "":
            self.report({'ERROR'}, f"Empty plan name")

            logger = logging.getLogger("myblenderlog")
            logger.info(f"Given plan name is empty")

            return {'FINISHED'}

        PlanEditor().openEditor(self.new_plan_name, self.drone_name)

        print(self.drone_name)

        logger = logging.getLogger("myblenderlog")
        logger.info(f"Editor panel was open: Creating {self.new_plan_name} plan")

        context.area.tag_redraw()

        return {'FINISHED'}

class ModifyPlanEditorOperator(bpy.types.Operator):
    bl_idname = "wm.modify_plan_editor"
    bl_label = "Modify"
    bl_description = "Modify plan"

    @classmethod
    def poll(cls, context):
        return not PlanEditor().isActive and \
               sceneModel.PlanCollection().getActive() is None and \
               len(sceneModel.PlanCollection()) > 0 and \
               not utilsAlgorithm.MarvelmindHandler().isRunning()

    def execute(self, context):
        plan_list = context.scene.plan_list
        plan_index = context.scene.plan_list_index

        if not 0 <= plan_index < len(plan_list):
            self.report({"ERROR"}, "No plan selected to modify")
            return {'FINISHED'}

        item = plan_list[plan_index]
        name = item.name
        drone_name = item.drone_name

        if name in sceneModel.PlanCollection():
            PlanEditor().openEditor(name, drone_name)
            logger = logging.getLogger("myblenderlog")
            logger.info(f"Editor panel was open: Modifying \"{name}\" plan")
        else:
            self.report({"ERROR"}, f"Plan list does not contain {name}")
            logger = logging.getLogger("myblenderlog")
            logger.info(f"Panel  ")

        context.area.tag_redraw()
        return {'FINISHED'}

class RemovePlanEditorOperator(bpy.types.Operator):
    bl_idname = "wm.remove_plan_editor"
    bl_label = "Remove"
    bl_description = "Remove plan"

    @classmethod
    def poll(cls, context):
        return not PlanEditor().isActive and \
               sceneModel.PlanCollection().getActive() is None and \
               len(sceneModel.PlanCollection()) > 0 and \
               not utilsAlgorithm.MarvelmindHandler().isRunning()

    def execute(self, context):
        plan_list = context.scene.plan_list
        plan_index = context.scene.plan_list_index

        if not 0 <= plan_index < len(plan_list):
            self.report({"ERROR"}, "No plan selected to remove")
            return {'FINISHED'}

        item = plan_list[plan_index]
        name = item.name

        if name in sceneModel.PlanCollection():
            sceneModel.PlanCollection().removePlan(name)
            plan_list.remove(plan_index)
            context.scene.plan_list_index = min(max(0, plan_index - 1), len(plan_list) - 1)
        else:
            self.report({"ERROR"}, f"Plan list does not contain {name}")

        logger = logging.getLogger("myblenderlog")
        logger.info(f"\"{name}\" plan was eliminated")

        return {'FINISHED'}

##############################################################################################
# Editing panel operators

class SavePlanEditorOperator(bpy.types.Operator):
    bl_idname = "wm.save_plan_editor"
    bl_label = "Save plan"
    bl_description = "Save plan"

    @classmethod
    def poll(cls, context):
        return not PlanValidatorOperator.any_cursor_collide()

    def execute(self, context):
        print("Close plan")

        name = PlanEditor().currentPlanID
        drone_name = PlanEditor().currentDroneID

        PlanEditor().savePlan()
        PlanEditor().closeEditor()

        if name not in context.scene.plan_list:
            item = context.scene.plan_list.add()
            item.name = name
            item.drone_name = drone_name

        context.area.tag_redraw()
        return {'FINISHED'}

class DiscardPlanOperator(bpy.types.Operator):
    bl_idname = "wm.discard_changes_plan"
    bl_label = "Discard changes"
    bl_description = "Discard changes in plan"

    def execute(self, context):
        PlanEditor().closeEditor()
        context.area.tag_redraw()
        return {'FINISHED'}

class AddPoseOperator(bpy.types.Operator):
    bl_idname = "wm.add_pose"
    bl_label = "Add pose"
    bl_description = "Add pose"

    def execute(self, context):
        print("Add pose")
        PlanEditor().addPose()
        return {'FINISHED'}

class RemovePoseOperator(bpy.types.Operator):
    bl_idname = "wm.remove_pose"
    bl_label = "Remove pose"
    bl_description = "Remove pose"

    @classmethod
    def poll(cls, context):
        obj_delete = [obj for obj in bpy.context.selected_objects if obj.name_full in PlanEditor()]
        return not PlanEditor().isEmpty and len(obj_delete) > 0

    def execute(self, context):
        print("Remove pose")
        PlanEditor().removePose()

        logger = logging.getLogger("myblenderlog")
        logger.info(f"Some poses was eliminated")
        return {'FINISHED'}

class InsertPoseBeforeOperator(bpy.types.Operator):
    bl_idname = "wm.insert_pose_before"
    bl_label = "Insert before selected pose"
    bl_description = "Insert pose before selected pose"

    @classmethod
    def poll(cls, context):
        obj_selected = [obj for obj in bpy.context.selected_objects if obj.name_full in PlanEditor()]
        return not PlanEditor().isEmpty and len(obj_selected) == 1

    def execute(self, context):
        print("Remove pose")
        PlanEditor().insertPose()

        logger = logging.getLogger("myblenderlog")
        logger.info(f"New pose was inserted")
        return {'FINISHED'}

################################################################################


class ActivePlanOperator(bpy.types.Operator):
    bl_idname = "wm.active_plan_operator"
    bl_label = "Select"
    bl_description = "Active plan"

    @classmethod
    def poll(cls, context):
        return not PlanEditor().isActive and \
                len(sceneModel.PlanCollection()) > 0 and \
                sceneModel.PlanCollection().getActive() is None and \
                not manualSimulationControl.ManualSimulationModalOperator.isRunning and \
                not utilsAlgorithm.MarvelmindHandler().isRunning()

    def execute(self, context):
        plan_list = context.scene.plan_list
        plan_index = context.scene.plan_list_index

        if not 0 <= plan_index < len(plan_list):
            self.report({"ERROR"}, "No plan selected to modify")
            return {'FINISHED'}

        item = plan_list[plan_index]
        name = item.name
        drone_name = item.drone_name

        drone = sceneModel.DronesCollection().get(drone_name)
        if drone is None:
            self.report({'INFO'}, f"{drone_name} not exists")
            return {'FINISHED'}

        if sceneModel.PlanCollection().getActive() is not None:
            sceneModel.PlanCollection().getActive().delete()
            sceneModel.PlanCollection().unsetActive()

        # draw plan
        sceneModel.DronesCollection().setActive(drone.meshID)
        sceneModel.PlanCollection().setActive(name)
        sceneModel.PlanCollection().getActive().draw()

        context.area.tag_redraw()
        return {'FINISHED'}


class DesactivePlanOperator(bpy.types.Operator):
    bl_idname = "wm.desactive_plan_operator"
    bl_label = "Deselect"
    bl_description = "Desactive plan"

    @classmethod
    def poll(cls, context):
        return not PlanEditor().isActive and \
               len(sceneModel.PlanCollection()) > 0 and \
               sceneModel.PlanCollection().getActive() is not None and \
               not manualSimulationControl.ManualSimulationModalOperator.isRunning and \
               not utilsAlgorithm.MarvelmindHandler().isRunning()

    def execute(self, context):
        plan_list = context.scene.plan_list
        plan_index = context.scene.plan_list_index

        if not 0 <= plan_index < len(plan_list):
            self.report({"ERROR"}, "No plan selected to modify")
            return {'FINISHED'}

        item = plan_list[plan_index]
        name = item.name
        drone_name = item.drone_name

        if sceneModel.PlanCollection().getActive() is None:
            return {'FINISHED'}

        sceneModel.DronesCollection().unsetActive()

        # remove plan
        sceneModel.PlanCollection().getActive().delete()
        sceneModel.PlanCollection().unsetActive()

        context.area.tag_redraw()
        return {'FINISHED'}


################################################################################

class TemporalShowPlanOperator(bpy.types.Operator):
    bl_idname = "wm.temporal_show_plan"
    bl_label = "Temporal Show Editor"

    def execute(self, context):
        print("See all plans:")
        print("Plan active: ", sceneModel.planCollection.PlanCollection().getActive())
        for plan in sceneModel.planCollection.PlanCollection():
            print(f"PlanID = { plan.planID } DroneID { plan.droneID }")
            for pose in plan:
                print(f"\t{ pose }")
        print("See all drones:")
        print("Drone active: ", sceneModel.dronesCollection.DronesCollection().getActive())
        for drone_id, drone_obj in sceneModel.dronesCollection.DronesCollection():
            print(f"Drone = {drone_id}, {drone_obj}")
        return {'FINISHED'}
