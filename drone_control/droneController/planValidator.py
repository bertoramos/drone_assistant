
import bpy
from mathutils import Vector

from drone_control.utilsAlgorithm import check_complete_overlap, check_simple_overlap, create_bmesh

def register():
    pass

def autounregister():
    pass

EPS = lambda context: context.scene.TOL

class PlanValidatorOperator(bpy.types.Operator):
    bl_idname = "wm.plan_validator_operator"
    bl_label = "Plan validator Operator"

    autoclose = False

    _timer = None
    _changes_cursor_dict = dict({})
    _changes_obj_dict = dict({})

    _cursor_colliding = dict({})
    
    _original_color = dict({})
    _alert_color = (1., 0., 0., 1.)

    _testable_objects = {'PATH_ELEMENTS'}
    _collisionable_objects = {'WALL', 'OBSTACLE', 'CEIL'}
    _need_to_clone = {'WALL', 'OBSTACLE'}

    @classmethod
    def any_cursor_collide(cls):
        any_colliding = len(PlanValidatorOperator._cursor_colliding) > 0
        all_set_empty = all([len(aset)==0 for aset in PlanValidatorOperator._cursor_colliding])
        return any_colliding and not all_set_empty

    @classmethod
    def _change_color(cls, obj):
        mat = obj.active_material
        if mat is None:
            mat = bpy.data.materials.new(obj.name_full + "_mat")
            obj.active_material = mat
        if obj.name_full not in PlanValidatorOperator._original_color:
            PlanValidatorOperator._original_color[obj.name_full] = mat.diffuse_color[:]
        mat.diffuse_color = PlanValidatorOperator._alert_color

    @classmethod
    def _set_original_color(cls, obj):
        mat = obj.active_material
        if mat is None:
            return
        if obj.name_full not in PlanValidatorOperator._original_color:
            return
        mat.diffuse_color = PlanValidatorOperator._original_color[obj.name_full]

    @classmethod
    def _clone_object(cls, obj):
        cube = None

        if obj.object_type == "WALL":
            bpy.ops.mesh.primitive_cube_add()
            cube = bpy.context.active_object

            cube.dimensions = obj.dimensions.xyz
            cube.location = obj.dimensions.xyz/2.0

            save_cursor_loc = bpy.context.scene.cursor.location.xyz
            bpy.context.scene.cursor.location = Vector((0,0,0))
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.context.scene.cursor.location = save_cursor_loc

            cube.location = obj.location.xyz
            cube.rotation_euler.z = obj.rotation_euler.z

            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

            bpy.context.scene.collection.objects.link(cube)

            cube.object_type = "TEMPORAL"

        if obj.object_type == "OBSTACLE":
            margin = obj.children[0]
            cube = margin.copy()
            cube.parent = None
            cube.object_type = "TEMPORAL"

            cube.location = obj.location.xyz
            cube.dimensions = obj.dimensions.xyz
            cube.rotation_euler = obj.rotation_euler

            bpy.context.scene.collection.objects.link(cube)
        
        return cube

    @classmethod
    def _get_from_objects(cls, obj_name):
        if obj_name in bpy.data.objects:
            return bpy.data.objects[obj_name]
        return None

    @classmethod
    def _check_overlap(cls, cursor_obj):
        overlap_list = []

        # Obtener el colisionador del objeto movido
        cursor_obj_collider = [e for e in cursor_obj.children if e.object_type == "ROBOT_MARGIN"][0]

        # Clona el colider
        cursor_obj_collider_clone = cursor_obj_collider.copy()
        cursor_obj_collider_clone.location = cursor_obj.location
        cursor_obj_collider_clone.rotation_euler = cursor_obj.rotation_euler
        cursor_obj_collider_clone.parent = None
        bpy.context.scene.collection.objects.link(cursor_obj_collider_clone)

        # Crea el bmesh para el chequeo de colisiones
        bm1 = create_bmesh(cursor_obj_collider_clone)

        for obj in bpy.data.objects:

            # Filtrar objetos con los que hay que comprobar la colision
            if obj.object_type not in PlanValidatorOperator._collisionable_objects:
                continue

            if obj.name_full != cursor_obj_collider.name_full:
                # Clonar el objeto si es necesario y crea el bmesh
                if obj.object_type in PlanValidatorOperator._need_to_clone:
                    cloned_obj = PlanValidatorOperator._clone_object(obj)
                    bm2 = create_bmesh(cloned_obj)
                else:
                    bm2 = create_bmesh(obj)

                # Comprobar colision
                if len(bm1.faces) > 1 and len(bm2.faces) > 1 and check_complete_overlap(bm1, bm2):
                    overlap_list.append(obj.name_full)
                
                if ( len(bm1.faces) == 1 or len(bm2.faces) == 1 ) and check_simple_overlap(bm1, bm2):
                    overlap_list.append(obj.name_full)

                # Eliminar el objeto clonado si fue clonado anteriormente
                if obj.object_type in PlanValidatorOperator._need_to_clone:
                    bpy.data.objects.remove(cloned_obj)
                
                bm2.free()

        # Elimina clon del collider
        bpy.data.objects.remove(cursor_obj_collider_clone)
        bm1.free()

        return overlap_list

    @classmethod
    def _modify_cursor_detected(cls, obj):
        # Salva nueva transformacion
        PlanValidatorOperator._changes_cursor_dict[obj.name_full] = (obj.location.copy(), obj.rotation_euler.copy(), obj.dimensions.copy())

        # Objetos con los que colisiona
        overlap_set = set(PlanValidatorOperator._check_overlap(obj))
        if len(overlap_set) > 0:
            # Si el cursor colisiona se cambia el color y almacena overlap_set
            PlanValidatorOperator._cursor_colliding[obj.name_full] = overlap_set
            PlanValidatorOperator._change_color(obj)
        else:
            # Si no colisiona se elimina porque el overlap_set esta vacio
            if obj.name_full in PlanValidatorOperator._cursor_colliding:
                del PlanValidatorOperator._cursor_colliding[obj.name_full]
            PlanValidatorOperator._set_original_color(obj)

    @classmethod
    def _del_cursor_detected(cls, obj_name):
        if obj_name in PlanValidatorOperator._changes_cursor_dict:
            del PlanValidatorOperator._changes_cursor_dict[obj_name]
        if obj_name in PlanValidatorOperator._cursor_colliding:
            del PlanValidatorOperator._cursor_colliding[obj_name]

    @classmethod
    def _new_cursor_detected(cls, obj):
        # Salva la transformacion del cursor
        PlanValidatorOperator._changes_cursor_dict[obj.name_full] = (obj.location.copy(), obj.rotation_euler.copy(), obj.dimensions.copy())

        overlap_set = set(PlanValidatorOperator._check_overlap(obj))
        # Si hay alguna colision cambia el color y almacena las colisiones con el cursor
        if len(overlap_set) > 0:
            PlanValidatorOperator._cursor_colliding[obj.name_full] = overlap_set
            PlanValidatorOperator._change_color(obj)

    @classmethod
    def _new_obj_detected(cls, obj):
        # Salva transformacion del objeto modificado
        PlanValidatorOperator._changes_obj_dict[obj.name_full] = (obj.location.copy(), obj.rotation_euler.copy(), obj.dimensions.copy())

        # Comprueba colision del objeto modificado con los cursores actuales
        for cursor_name in list(PlanValidatorOperator._changes_cursor_dict):
            cursor_obj = PlanValidatorOperator._get_from_objects(cursor_name)
            if cursor_obj is not None:
                # Objetos con los que colisiona
                overlap_set = set(PlanValidatorOperator._check_overlap(cursor_obj))
                if len(overlap_set) > 0:
                    # Si el cursor colisiona se cambia el color y almacena overlap_set
                    PlanValidatorOperator._cursor_colliding[cursor_obj.name_full] = overlap_set
                    PlanValidatorOperator._change_color(cursor_obj)
                else:
                    # Si no colisiona se elimina porque el overlap_set esta vacio
                    if cursor_obj.name_full in PlanValidatorOperator._cursor_colliding:
                        del PlanValidatorOperator._cursor_colliding[cursor_obj.name_full]
                    PlanValidatorOperator._set_original_color(cursor_obj)


    @classmethod
    def _del_obj_detected(cls, obj_name):
        del PlanValidatorOperator._changes_obj_dict[obj_name]
        for cursor_name in list(PlanValidatorOperator._cursor_colliding):
            if obj_name in PlanValidatorOperator._cursor_colliding[cursor_name]:
                PlanValidatorOperator._cursor_colliding[cursor_name].remove(obj_name)
                if len(PlanValidatorOperator._cursor_colliding[cursor_name]) == 0:
                    del PlanValidatorOperator._cursor_colliding[cursor_name]
                    cursor_obj = PlanValidatorOperator._get_from_objects(cursor_name)
                    if cursor_obj is not None:
                        PlanValidatorOperator._set_original_color(cursor_obj)

    @classmethod
    def _modify_obj_detected(cls, obj):
        # Salva transformacion del objeto modificado
        PlanValidatorOperator._changes_obj_dict[obj.name_full] = (obj.location.copy(), obj.rotation_euler.copy(), obj.dimensions.copy())

        # Comprueba colision del objeto modificado con los cursores actuales
        for cursor_name in list(PlanValidatorOperator._changes_cursor_dict):
            cursor_obj = PlanValidatorOperator._get_from_objects(cursor_name)
            if cursor_obj is not None:
                # Objetos con los que colisiona
                overlap_set = set(PlanValidatorOperator._check_overlap(cursor_obj))
                if len(overlap_set) > 0:
                    # Si el cursor colisiona se cambia el color y almacena overlap_set
                    PlanValidatorOperator._cursor_colliding[cursor_obj.name_full] = overlap_set
                    PlanValidatorOperator._change_color(cursor_obj)
                else:
                    # Si no colisiona se elimina porque el overlap_set esta vacio
                    if cursor_obj.name_full in PlanValidatorOperator._cursor_colliding:
                        del PlanValidatorOperator._cursor_colliding[cursor_obj.name_full]
                    PlanValidatorOperator._set_original_color(cursor_obj)

    def modal(self, context, event):

        if event.type in {'ESC'} or PlanValidatorOperator.autoclose:
            PlanValidatorOperator.autoclose = False
            PlanValidatorOperator._cursor_colliding = dict({})
            PlanValidatorOperator._changes_cursor_dict = dict({})
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':

            # Comprueba modificaciones de los cursores
            filter_obj = [e for e in bpy.data.objects if e.object_type in self._testable_objects]

            for o in filter_obj:
                if o.name_full in PlanValidatorOperator._changes_cursor_dict:
                    loc_len = (PlanValidatorOperator._changes_cursor_dict[o.name_full][0] - o.location).length
                    rot_len = (Vector(PlanValidatorOperator._changes_cursor_dict[o.name_full][1][:]) - Vector(o.rotation_euler[:])).length
                    dim_len = (PlanValidatorOperator._changes_cursor_dict[o.name_full][2] - o.dimensions).length
                    if loc_len > EPS(context) or rot_len > EPS(context) or dim_len > EPS(context):
                        PlanValidatorOperator._modify_cursor_detected(o)

            # Comprueba si se añade o modifica un obstaculo
            filter_obj = [e for e in bpy.data.objects if e.object_type in self._collisionable_objects]

            for o in filter_obj:
                # Se añade un obstaculo
                if o.name_full not in PlanValidatorOperator._changes_obj_dict:
                    PlanValidatorOperator._new_obj_detected(o)

                # Se modifica el obstaculo
                if o.name_full in PlanValidatorOperator._changes_obj_dict:
                    loc_len = (PlanValidatorOperator._changes_obj_dict[o.name_full][0] - o.location).length
                    rot_len = (Vector(PlanValidatorOperator._changes_obj_dict[o.name_full][1][:]) - Vector(o.rotation_euler[:])).length
                    dim_len = (PlanValidatorOperator._changes_obj_dict[o.name_full][2] - o.dimensions).length

                    if loc_len > EPS(context) or rot_len > EPS(context) or dim_len > EPS(context):
                        PlanValidatorOperator._modify_obj_detected(o)

            # Comprueba si se elimina un obstaculo
            for o_name in list(PlanValidatorOperator._changes_obj_dict):
                if o_name not in bpy.data.objects:
                    PlanValidatorOperator._del_obj_detected(o_name)
        
        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
