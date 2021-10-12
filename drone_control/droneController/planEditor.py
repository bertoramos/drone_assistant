
import bpy
import mathutils
import math

from drone_control.patternModel.singletonModel import Singleton

from .planValidator import PlanValidatorOperator

from drone_control.sceneModel import PlanModel
from drone_control.sceneModel import create_cursor, remove_cursor
from drone_control.sceneModel import Pose
from drone_control.sceneModel import PlanCollection, DronesCollection
from drone_control.utilsAlgorithm import draw_text

def _create_plan(planID, droneID, mesh_names):
    plan = PlanModel(planID, droneID)
    for name in mesh_names:
        cursor_obj = bpy.data.objects[name]
        pose = Pose.fromVector(cursor_obj.location, cursor_obj.rotation_euler)
        plan.addPose(pose)
    return plan

def _redraw_plan(mesh_names, drone_dim, margin_dim, margin_scale):
    newList = []
    for pid, name in enumerate(mesh_names):
        cursor_obj = bpy.data.objects[name]
        cursor_name = create_cursor(cursor_obj.location, cursor_obj.rotation_euler, drone_dim, margin_dim, margin_scale, pid)
        remove_cursor(bpy.data.objects[name])
        newList.append(cursor_name)
        PlanValidatorOperator._new_cursor_detected(bpy.data.objects[cursor_name])
    return newList

class PlanEditor(metaclass=Singleton):

    def __init__(self):
        self.__cursor_mesh_id = None

        self.__current_planID = None
        self.__current_droneID = None
        self.__poses_mesh_names = []

    def openEditor(self, planID: str, droneID: str):
        bpy.ops.wm.plan_validator_operator('INVOKE_DEFAULT')

        if planID not in PlanCollection():
            # Nuevo plan
            self.__current_planID = planID
            self.__current_droneID = droneID
        else:
            # Busca plan
            plan = PlanCollection().getPlan(planID)
            self.__current_planID = plan.planID
            self.__current_droneID = plan.droneID

            drone = DronesCollection().get(self.__current_droneID)
            drone_obj = bpy.data.objects[drone.meshID] if drone.meshID in bpy.data.objects else None
            collider_obj = bpy.data.objects[drone.colliderID] if drone.colliderID in bpy.data.objects else None

            if drone_obj is None or collider_obj is None:
                return

            # Lo carga en el editor
            for position_num, pose in enumerate(plan):
                cursor_name = create_cursor(pose.location, pose.rotation, drone_obj.dimensions.copy(), collider_obj.dimensions.copy(), collider_obj.scale.copy(), position_num)
                self.__poses_mesh_names.append(cursor_name)
                PlanValidatorOperator._new_cursor_detected(bpy.data.objects[cursor_name])


    def closeEditor(self):
        PlanValidatorOperator.autoclose = True

        self.__current_planID = None
        self.__current_droneID = None
        for name in self.__poses_mesh_names:
            remove_cursor(bpy.data.objects[name])
        self.__poses_mesh_names.clear()


    def savePlan(self):
        if self.__current_planID is not None:
            # Recorre poses y las almacena en un nuevo plan
            plan = _create_plan(self.__current_planID, self.__current_droneID, self.__poses_mesh_names)
            # Reemplaza el plan en la coleccion por el nuevo
            #  o crea uno nuevo si no existe
            PlanCollection().addPlan(plan)

    def insertPose(self):
        obj_selected = [obj for obj in bpy.context.selected_objects if obj.name_full in self.__poses_mesh_names]
        if len(obj_selected) > 1:
            return
        obj_selected = obj_selected[0]
        for obj_i, name in enumerate(self.__poses_mesh_names):
            if name == obj_selected.name_full:
                prev_obj = self.__poses_mesh_names[obj_i-1] if obj_i-1 >= 0 else ""

                if prev_obj == "":
                    loc = obj_selected.location - mathutils.Vector((1,1,1))
                    rot = obj_selected.rotation_euler
                else:
                    loc = (bpy.data.objects[prev_obj].location + obj_selected.location)/2.0
                    rot = obj_selected.rotation_euler

                drone = DronesCollection().get(self.__current_droneID)
                drone_obj = bpy.data.objects[drone.meshID] if drone.meshID in bpy.data.objects else None
                collider_obj = bpy.data.objects[drone.colliderID] if drone.colliderID in bpy.data.objects else None

                if drone_obj is None or collider_obj is None:
                    return

                cursor_name = create_cursor(loc, rot, drone_obj.dimensions.copy(), collider_obj.dimensions.copy(), collider_obj.scale.copy(), obj_i)
                self.__poses_mesh_names.insert(obj_i, cursor_name)

                bpy.context.view_layer.objects.active = bpy.data.objects[cursor_name]
                bpy.data.objects[cursor_name].select_set(True)

                self.__poses_mesh_names = _redraw_plan(self.__poses_mesh_names, drone_obj.dimensions.copy(), collider_obj.dimensions.copy(), collider_obj.scale.copy())

                PlanValidatorOperator._new_cursor_detected(bpy.data.objects[cursor_name])
                break

    def addPose(self):
        last_location = None
        last_rotation = None
        position_num  = 0
        if len(self.__poses_mesh_names) == 0:
            last_location = mathutils.Vector((0, 0, 0))
            last_rotation = mathutils.Euler((0, 0, 0))
            position_num = 0
        else:
            last_obj = bpy.data.objects[self.__poses_mesh_names[-1]]
            last_location = last_obj.location
            last_rotation = mathutils.Euler((0, 0, 0)) #last_obj.rotation_euler
            position_num = len(self.__poses_mesh_names)

        drone = DronesCollection().get(self.__current_droneID)
        drone_obj = bpy.data.objects[drone.meshID] if drone.meshID in bpy.data.objects else None
        collider_obj = bpy.data.objects[drone.colliderID] if drone.colliderID in bpy.data.objects else None

        if drone_obj is None or collider_obj is None:
            return

        cursor_name = create_cursor(last_location, last_rotation, drone_obj.dimensions.copy(), collider_obj.dimensions.copy(), collider_obj.scale.copy(), position_num)
        self.__poses_mesh_names.append(cursor_name)

        PlanValidatorOperator._new_cursor_detected(bpy.data.objects[cursor_name])

        bpy.context.view_layer.objects.active = bpy.data.objects[cursor_name]
        bpy.data.objects[cursor_name].select_set(True)

    def removePose(self):
        # Elimina las poses seleccionadas en la escena
        obj_delete = [obj for obj in bpy.context.selected_objects if obj.name_full in self.__poses_mesh_names]
        for obj in obj_delete:
            obj_name = obj.name_full
            remove_cursor(bpy.data.objects[obj_name])
            self.__poses_mesh_names.remove(obj_name)
            PlanValidatorOperator._del_cursor_detected(obj_name)

        drone = DronesCollection().get(self.__current_droneID)
        drone_obj = bpy.data.objects[drone.meshID] if drone.meshID in bpy.data.objects else None
        collider_obj = bpy.data.objects[drone.colliderID] if drone.colliderID in bpy.data.objects else None

        if drone_obj is None or collider_obj is None:
            return

        self.__poses_mesh_names = _redraw_plan(self.__poses_mesh_names, drone_obj.dimensions.copy(), collider_obj.dimensions.copy(), collider_obj.scale.copy())

    def __contains__(self, value):
        return value in self.__poses_mesh_names

    def currentPlanID():
        doc = "The currentPlanID property."
        def fget(self):
            return self.__current_planID
        return locals()
    currentPlanID = property(**currentPlanID())

    def currentDroneID():
        doc = "The currentDroneID property"
        def fget(self):
            return self.__current_droneID
        return locals()
    currentDroneID = property(**currentDroneID())

    def isActive():
        doc = "The isActive property."
        def fget(self):
            return self.__current_planID is not None
        return locals()
    isActive = property(**isActive())

    def isEmpty():
        doc = "The isEmpty property."
        def fget(self):
            return len(self.__poses_mesh_names) == 0
        return locals()
    isEmpty = property(**isEmpty())
