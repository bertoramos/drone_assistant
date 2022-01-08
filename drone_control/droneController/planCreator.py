
import bpy
import logging

import os
import json
import pathlib

from bpy_extras.io_utils import ExportHelper

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
        from .plan_generator import PlanGeneratorModalOperator

        return not PlanEditor().isActive and \
               sceneModel.PlanCollection().getActive() is None and \
               len(sceneModel.DronesCollection()) > 0 and \
               not PlanGeneratorModalOperator.isRunning

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

def export_plan(path, name, data_poses):
    if not os.access(path, os.W_OK):
        return False

    with open(path / name, 'w') as outfile:
        try:
            json.dump(data_poses, outfile)
            return True
        except Exception as ex:
            print(ex)
            return False

def read_plan(path, name):
    if not (path / name).is_file():
        return None

    with open(path / name, 'r') as outfile:
        data = json.load(outfile)
        return data
    return None

class ExportPlanOperator(bpy.types.Operator, ExportHelper):
    bl_idname = "wm.export_plan_operator"
    bl_label = "Export"
    bl_description = "Export plan"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        return not PlanEditor().isActive and \
                len(sceneModel.PlanCollection()) > 0 and \
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
        
        plan = sceneModel.PlanCollection().getPlan(name)
        if plan is None:
            self.report({'INFO'}, f"{name} not exists")
            return {'FINISHED'}
        
        
        poses = []
        for p in list(iter(plan)):
            x = p.location.x
            y = p.location.y
            z = p.location.z
            rx = p.rotation.x
            ry = p.rotation.y
            rz = p.rotation.z
            poses.append([x, y, z, rx, ry, rz])
        
        """
        drone.address = (12, 13)
        drone.serverAddress = '192.168.0.16'
        drone.serverPort = 4445
        drone.clientAddress = '192.168.0.24'
        drone.clientPort = 5558
        """
        drone_mesh = bpy.data.objects[drone.meshID]
        drone_collider = bpy.data.objects[drone.colliderID]

        drone_pose = drone.pose

        data_poses = {
            'poses': poses,
            'drone': {
                'pose': [drone_pose.location.x, drone_pose.location.y, drone_pose.location.z, drone_pose.rotation.x, drone_pose.rotation.y, drone_pose.rotation.z],
                'dimension': [drone_collider.dimensions.x, drone_collider.dimensions.y, drone_collider.dimensions.z],
                'left_beacon_address': drone.address[0],
                'right_beacon_address': drone.address[1],
                'server_address': drone.serverAddress,
                'server_port': drone.serverPort,
                'client_address': drone.clientAddress,
                'client_port': drone.clientPort
            }
        }

        filepath_str = self.filepath
        filepath = pathlib.Path(filepath_str)
        path = filepath.parent
        name = pathlib.Path(filepath.name)

        if not export_plan(path, name, data_poses):
            self.report({'ERROR'}, f"Cannot write in {str(path / name)}")
        else:
            self.report({'INFO'}, f"Exported path in {str(path / name)}")

        return {'FINISHED'}


class ImportPlanOperator(bpy.types.Operator, ExportHelper):
    bl_idname = "wm.import_plan_operator"
    bl_label = "Import"
    bl_description = "Import plan"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    new_plan_name : bpy.props.StringProperty(name="Plan name")
    new_drone_name : bpy.props.StringProperty(name="Drone name")

    def draw(self, context):
        self.layout.prop(self, "new_plan_name")
        self.layout.prop(self, "new_drone_name")

    @classmethod
    def poll(cls, context):
        return not manualSimulationControl.ManualSimulationModalOperator.isRunning and \
                not utilsAlgorithm.MarvelmindHandler().isRunning()

    def execute(self, context):
        filepath_str = self.filepath
        filepath = pathlib.Path(filepath_str)
        path = filepath.parent
        name = pathlib.Path(filepath.name)

        context.area.tag_redraw()

        plan_name = self.new_plan_name
        drone_name = self.new_drone_name

        if plan_name == "":
            self.report({"ERROR"}, "No name has been given to the new plan")
            return {'FINISHED'}
        if drone_name == "":
            self.report({"ERROR"}, "No name has been given to the new drone")
            return {'FINISHED'}

        if plan_name in sceneModel.PlanCollection() and drone_name in sceneModel.DronesCollection():
            self.report({'ERROR'}, f"Plan {plan_name} and drone {drone_name} already exist")
            return {'FINISHED'}
        if plan_name in sceneModel.PlanCollection():
            self.report({"ERROR"}, f"Plan {plan_name} already exists")
            return {'FINISHED'}
        if drone_name in sceneModel.DronesCollection():
            self.report({"ERROR"}, f"Drone {drone_name} already exists")
            return {'FINISHED'}
        
        if ( json_poses := read_plan(path, name) ) is None:
            self.report({'ERROR'}, f"Cannot read {str(path / name)}")
        else:
            self.report({'INFO'}, f"Path loaded from {str(path / name)}")

        print(json_poses)

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
