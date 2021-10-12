

import bpy
import bmesh
from mathutils import Vector, Euler

import numpy as np
from drone_control import sceneModel

def create_bmesh(obj):
    tmp = obj.copy()
    tmp.data = obj.data.copy()
    bpy.context.scene.collection.objects.link(tmp)

    [o.select_set(False) for o in bpy.data.objects]
    tmp.select_set(True)
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
    tmp.select_set(False)

    bm = bmesh.new()
    bm.from_mesh(tmp.data)
    bm.transform(tmp.matrix_world)

    bpy.data.objects.remove(tmp, do_unlink=True)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    return bm

def create_plan(self, context, obj, step_dist=1.):
    rot = obj.rotation_euler.copy()
    obj.rotation_euler = Euler((0, 0, 0))
    
    bm = create_bmesh(obj)
    verts = np.array([list(e.co.copy()[:]) for e in bm.verts])
    
    xmin = np.min(verts[:, 0])
    xmax = np.max(verts[:, 0])
    ymin = np.min(verts[:, 1])
    ymax = np.max(verts[:, 1])
    zmin = np.min(verts[:, 2])
    zmax = np.max(verts[:, 2])
    
    points = []
    
    X = np.mgrid[xmin:xmax:step_dist]
    Y = np.mgrid[ymin:ymax:step_dist]
    Z = np.mgrid[zmin:zmax:step_dist]

    X = np.concatenate( ( X, np.array([xmax]) ) ) if abs(xmax - X[-1]) > 0.1 else X
    Y = np.concatenate( ( Y, np.array([ymax]) ) ) if abs(ymax - Y[-1]) > 0.1 else Y
    Z = np.concatenate( ( Z, np.array([zmax]) ) ) if abs(zmax - Z[-1]) > 0.1 else Z

    xvals, yvals, zvals = np.meshgrid(X, Y, Z)
    xvals = xvals.reshape(1, -1)[0]
    yvals = yvals.reshape(1, -1)[0]
    zvals = zvals.reshape(1, -1)[0]

    #xvals = np.concatenate( ( xvals, np.array([xmax]) ) ) if abs(xmax - xvals[-1]) > 0 else xvals
    #yvals = np.concatenate( ( yvals, np.array([ymax]) ) ) if abs(ymax - yvals[-1]) > 0 else yvals
    #zvals = np.concatenate( ( zvals, np.array([zmax]) ) ) if abs(zmax - zvals[-1]) > 0 else zvals

    for xi, yi, zi in zip(xvals, yvals, zvals):
        # pname = create_point(xi, yi, zi)
        points.append([xi, yi, zi])
    
    return np.array(points)


class PlanGeneratorModalOperator(bpy.types.Operator):
    bl_idname = "scene.plan_generator_modal"
    bl_label = "GeneratorModal"

    obj_name = None
    collider_name = None

    def create_area(self, context):
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, location=(1, 1, 1))
        self.obj_name = context.active_object.name_full
        
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, location=(1, 1, 1))
        self.collider_name = context.active_object.name_full

        if bpy.data.objects[self.collider_name].active_material is None:
            mat = bpy.data.materials.new(self.collider_name + "_material")
            bpy.data.objects[self.collider_name].active_material = mat
            mat.diffuse_color = Vector((0, 0, 0, 0.2))
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects[self.obj_name]
        bpy.data.objects[self.obj_name].select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.data.objects[self.obj_name].lock_rotation[:] = (True, True, True)

        bpy.context.view_layer.objects.active = bpy.data.objects[self.collider_name]
        bpy.data.objects[self.collider_name].select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.data.objects[self.obj_name].lock_rotation[:] = (True, True, True)
        bpy.data.objects[self.collider_name].hide_select = True

        #bpy.data.objects[self.collider_name].parent = bpy.data.objects[self.obj_name]
        #bpy.data.objects[self.collider_name].parent.keep_transform = bpy.data.objects[self.obj_name]
        #bpy.data.objects[self.collider_name].matrix_parent_inverse = bpy.data.objects[self.obj_name].matrix_world.inverted()

        #bpy.data.objects[self.collider_name].location = bpy.data.objects[self.obj_name].location
        #bpy.data.objects[self.collider_name].rotation_euler = bpy.data.objects[self.obj_name].rotation_euler

        drone = sceneModel.DronesCollection().activeDrone
        self.dim = bpy.data.objects[drone.colliderID].dimensions.copy()
        # TODO: ESTABLECER LOCALIZACIÓN Y DIMENSION DEL COLLIDER COPIANDO EL DEL BLOQUE

        bpy.data.objects[self.collider_name].dimensions = bpy.data.objects[self.obj_name].dimensions + self.dim

        bpy.data.objects[self.collider_name].location -= self.dim/2
    
    def modal(self, context, event):
        if event.type == "RET":
            # create_plan(self, context, GeneratorModalOperator.obj)
            # bpy.data.objects.remove(GeneratorModalOperator.obj)
            # print("RETURN")
            return {'FINISHED'}
        if event.type == 'TIMER':
            # TODO: ESTABLECER LOCALIZACIÓN Y DIMENSION DEL COLLIDER COPIANDO EL DEL BLOQUE
            bpy.data.objects[self.collider_name].location = bpy.data.objects[self.obj_name].location
            scale = bpy.data.objects[self.obj_name].scale
            scale = Vector((1 if scale.x > 0 else -1, 1 if scale.y > 0 else -1, 1 if scale.z > 0 else -1))
            dimension = bpy.data.objects[self.obj_name].dimensions
            bpy.data.objects[self.collider_name].dimensions = Vector((scale.x*dimension.x, scale.y*dimension.y, scale.z*dimension.z)) + self.dim
            bpy.data.objects[self.collider_name].location -= self.dim/2

        return {'PASS_THROUGH'}

    def execute(self, context):
        print("EXECUTE")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        
        self.create_area(context)

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

