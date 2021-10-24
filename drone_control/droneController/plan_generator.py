

import bpy
import bmesh
from mathutils import Vector, Euler
import numpy as np

# import networkx as nx
# import networkx.algorithms.approximation.traveling_salesman as tsp

from drone_control import sceneModel
from drone_control.utilsAlgorithm import check_complete_overlap, check_simple_overlap, create_bmesh
from .planCreator import PlanEditor


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

def create_points(context, obj, step_dist=1.):
    obj.rotation_euler = Euler((0, 0, 0))
    
    bm = create_bmesh(obj)
    verts = np.array([list(e.co.copy()[:]) for e in bm.verts])
    
    xmin = np.min(verts[:, 0])
    xmax = np.max(verts[:, 0])
    ymin = np.min(verts[:, 1])
    ymax = np.max(verts[:, 1])
    zmin = np.min(verts[:, 2])
    zmax = np.max(verts[:, 2])
    
    X = np.mgrid[xmin:xmax:step_dist]
    Y = np.mgrid[ymin:ymax:step_dist]
    Z = np.mgrid[zmin:zmax:step_dist]

    X = np.concatenate( ( X, np.array([xmax]) ) ) if abs(xmax - X[-1]) > 0.1 else X
    Y = np.concatenate( ( Y, np.array([ymax]) ) ) if abs(ymax - Y[-1]) > 0.1 else Y
    Z = np.concatenate( ( Z, np.array([zmax]) ) ) if abs(zmax - Z[-1]) > 0.1 else Z

    xvals, yvals, zvals = np.meshgrid(X, Y, Z)

    return xvals, yvals, zvals

"""
def create_new_plan(X, Y, Z):
    G = nx.Graph()
    points = []
    position = {}

    # xvals = X.reshape(1, -1)[0]
    # yvals = Y.reshape(1, -1)[0]
    # zvals = Z.reshape(1, -1)[0]

    ilen = X.shape[0]
    jlen = X.shape[1]
    klen = X.shape[2]

    num = 0
    for i in range(ilen):
        for j in range(jlen):
            for k in range(klen):
                xi = X[i,j,k]
                yi = Y[i,j,k]
                zi = Z[i,j,k]
                points.append([num, xi, yi, zi])
                position[(i,j,k)] = num
                G.add_node(num, pos=(xi, yi, zi))

                num+=1
    
    test_range = lambda pos: pos[0] in range(ilen) and pos[1] in range(jlen) and pos[2] in range(klen)

    num = 0
    for i in range(ilen):
        for j in range(jlen):
            for k in range(klen):
                xi = X[i,j,k]
                yi = Y[i,j,k]
                zi = Z[i,j,k]
                current_pos = position[(i, j, k)]

                # Agregar aristas
                v = (i-1, j, k)
                if test_range(v):
                    xv, yv, zv = X[v], Y[v], Z[v]
                    neig_pos = position[v]
                    if (current_pos, neig_pos) not in G.edges:
                        dist = ( Vector((xi, yi, zi)) - Vector((xv,yv,zv)) ).length
                        G.add_edge(current_pos, neig_pos, weight=dist)

                v = (i+1, j, k)
                if test_range(v):
                    xv, yv, zv = X[v], Y[v], Z[v]
                    neig_pos = position[v]
                    if (current_pos, neig_pos) not in G.edges:
                        dist = ( Vector((xi, yi, zi)) - Vector((xv,yv,zv)) ).length
                        G.add_edge(current_pos, neig_pos, weight=dist)
                
                v = (i, j-1, k)
                if test_range(v):
                    xv, yv, zv = X[v], Y[v], Z[v]
                    neig_pos = position[v]
                    if (current_pos, neig_pos) not in G.edges:
                        dist = ( Vector((xi, yi, zi)) - Vector((xv,yv,zv)) ).length
                        G.add_edge(current_pos, neig_pos, weight=dist)
                
                v = (i, j+1, k)
                if test_range(v):
                    xv, yv, zv = X[v], Y[v], Z[v]
                    neig_pos = position[v]
                    if (current_pos, neig_pos) not in G.edges:
                        dist = ( Vector((xi, yi, zi)) - Vector((xv,yv,zv)) ).length
                        G.add_edge(current_pos, neig_pos, weight=dist)
                
                v = (i, j, k-1)
                if test_range(v):
                    xv, yv, zv = X[v], Y[v], Z[v]
                    neig_pos = position[v]
                    if (current_pos, neig_pos) not in G.edges:
                        dist = ( Vector((xi, yi, zi)) - Vector((xv,yv,zv)) ).length
                        G.add_edge(current_pos, neig_pos, weight=dist)
                
                v = (i, j, k+1)
                if test_range(v):
                    xv, yv, zv = X[v], Y[v], Z[v]
                    neig_pos = position[v]
                    if (current_pos, neig_pos) not in G.edges:
                        dist = ( Vector((xi, yi, zi)) - Vector((xv,yv,zv)) ).length
                        G.add_edge(current_pos, neig_pos, weight=dist)
                
                num += 1
    path = tsp.traveling_salesman_problem(G, cycle=False)
    print("edges", G.edges)
    print("path", path)
    return points

"""

def create_plan(X,Y,Z):

    points = []

    XN = X.shape[0]
    YN = X.shape[1]
    ZN = X.shape[2]

    num = 0
    for i in range(XN):
        for j in range(YN):
            for k in range(ZN):
                xi = X[i,j,k]
                yi = Y[i,j,k]
                zi = Z[i,j,k]
                points.append([num, xi, yi, zi])
                num += 1
    
    rev_j = False
    rev_x = False
    
    # Buscar si es posible optimizar
    opt_points = []
    num = 0
    for k in reversed(range(ZN)):
        jlist = range(YN) if not rev_j else reversed(range(YN))
        for j in jlist:
            xlist = range(XN) if not rev_x else reversed(range(XN))
            for i in xlist:
                xi = X[i, j, k]
                yi = Y[i, j, k]
                zi = Z[i, j, k]
                opt_points.append([num, xi, yi, zi])
                num += 1
            rev_x = not rev_x
        rev_j = not rev_j
    
    return opt_points

class PlanGeneratorModalOperator(bpy.types.Operator):
    bl_idname = "scene.plan_generator_modal"
    bl_label = "Plan Generator"

    
    _collisionable_objects = {'WALL', 'OBSTACLE', 'CEIL'}
    _need_to_clone = {'WALL', 'OBSTACLE'}

    obj_name = None
    collider_name = None
    isColliding = False

    _original_color = None
    _alert_color = (1., 0., 0., 1.)

    isRunning = False

    def _change_color(cls, obj):
        mat = obj.active_material
        if mat is None:
            mat = bpy.data.materials.new(obj.name_full + "_mat")
            obj.active_material = mat
        if PlanGeneratorModalOperator._original_color is None:
            PlanGeneratorModalOperator._original_color = mat.diffuse_color[:]
        mat.diffuse_color = PlanGeneratorModalOperator._alert_color
    
    def _set_original_color(cls, obj):
        mat = obj.active_material
        if mat is None:
            return
        if PlanGeneratorModalOperator._original_color is None:
            return
        mat.diffuse_color = PlanGeneratorModalOperator._original_color

    def _clone_object(self, obj):
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

    def _check_overlap(self, collider_obj):
        overlap_list = []

        # Crea el bmesh para el chequeo de colisiones
        bm1 = create_bmesh(collider_obj)

        for obj in bpy.data.objects:

            # Filtrar objetos con los que hay que comprobar la colision
            if obj.object_type not in PlanGeneratorModalOperator._collisionable_objects:
                continue

            if obj.name_full != collider_obj.name_full:
                # Clonar el objeto si es necesario y crea el bmesh
                if obj.object_type in PlanGeneratorModalOperator._need_to_clone:
                    cloned_obj = self._clone_object(obj)
                    bm2 = create_bmesh(cloned_obj)
                else:
                    bm2 = create_bmesh(obj)

                # Comprobar colision
                if len(bm1.faces) > 1 and len(bm2.faces) > 1 and check_complete_overlap(bm1, bm2):
                    overlap_list.append(obj.name_full)
                
                if ( len(bm1.faces) == 1 or len(bm2.faces) == 1 ) and check_simple_overlap(bm1, bm2):
                    overlap_list.append(obj.name_full)

                # Eliminar el objeto clonado si fue clonado anteriormente
                if obj.object_type in PlanGeneratorModalOperator._need_to_clone:
                    bpy.data.objects.remove(cloned_obj)
                
                bm2.free()
        
        # Elimina clon del collider
        bm1.free()

        return overlap_list

    def create_area(self, context):
        # Create area
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, location=(1, 1, 1))
        self.obj_name = context.active_object.name_full
        
        # Create margin
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, location=(1, 1, 1))
        self.collider_name = context.active_object.name_full

        # Add material to margin
        if bpy.data.objects[self.collider_name].active_material is None:
            mat = bpy.data.materials.new(self.collider_name + "_material")
            bpy.data.objects[self.collider_name].active_material = mat
            mat.diffuse_color = Vector((0, 0, 0, 0.2))
        
        # Set origin to corner of area
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects[self.obj_name]
        bpy.data.objects[self.obj_name].select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        # Lock objects
        bpy.data.objects[self.obj_name].lock_rotation[:] = (True, True, True)
        bpy.data.objects[self.collider_name].hide_select = True
        bpy.data.objects[self.obj_name].protected = True
        bpy.data.objects[self.collider_name].protected = True
        
        # Move margin to initial position
        area_location = bpy.data.objects[self.obj_name].location.copy()
        area_scale = bpy.data.objects[self.obj_name].scale.copy()
        area_dim = bpy.data.objects[self.obj_name].dimensions.copy()
        
        drone = sceneModel.DronesCollection().get(self.drone_name)
        self.dim = bpy.data.objects[drone.colliderID].dimensions.copy()
        
        self.move_margin(area_location, area_scale, area_dim)
        # self.last_loc = bpy.data.objects[self.obj_name].location.copy()
        # self.last_dim = bpy.data.objects[self.obj_name].dimensions.copy()
    
    def move_margin(self, area_location, area_scale, area_dim):
        xloc = area_location.x + np.sign(area_scale.x)*(area_dim.x/2.0)
        yloc = area_location.y + np.sign(area_scale.y)*(area_dim.y/2.0)
        zloc = area_location.z + np.sign(area_scale.z)*(area_dim.z/2.0)
        loc = Vector((xloc, yloc, zloc))
        bpy.data.objects[self.collider_name].location = loc

        xdim = area_dim.x + self.dim.x
        ydim = area_dim.y + self.dim.y
        zdim = area_dim.z + self.dim.z
        bpy.data.objects[self.collider_name].dimensions = Vector((xdim, ydim, zdim))
            
        self.last_loc = area_location
        self.last_dim = area_dim
    

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
    step_dist : bpy.props.FloatProperty(
        name="Step distance",
        default=1.,
        min=0.1
    )

    def draw(self, context):
        self.layout.prop(self, "new_plan_name")
        self.layout.prop(self, "drone_name")
        self.layout.prop(self, "step_dist")
    
    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D" and \
               len(sceneModel.DronesCollection()) > 0 and \
               sceneModel.PlanCollection().getActive() is None and \
               not PlanEditor().isActive and \
               not PlanGeneratorModalOperator.isRunning
    
    def modal(self, context, event):

        if event.type == "ESC":
            bpy.data.objects.remove(bpy.data.objects[self.obj_name])
            bpy.data.objects.remove(bpy.data.objects[self.collider_name])

            PlanGeneratorModalOperator.isRunning = False
            return {'FINISHED'}

        if event.type == "SPACE":
            # create_plan(self, context, GeneratorModalOperator.obj)
            # bpy.data.objects.remove(GeneratorModalOperator.obj)
            # print("RETURN")
            if self.isColliding:
                self.report({'ERROR'}, "Cannot create a new plan")
                return {'PASS_THROUGH'}
            
            X, Y, Z = create_points(context, bpy.data.objects[self.obj_name], step_dist=self.step_dist)
            points = create_plan(X, Y, Z)
            
            planName = self.new_plan_name
            droneID = self.drone_name
            plan = sceneModel.PlanModel(planName, droneID)
            for p in points:
                pose = sceneModel.Pose(p[1], p[2], p[3], 0, 0, 0)
                plan.addPose(pose)
            sceneModel.PlanCollection().addPlan(plan)


            if planName not in context.scene.plan_list:
                item = context.scene.plan_list.add()
                item.name = planName
                item.drone_name = droneID

            context.area.tag_redraw()

            # bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(p[0], p[1], p[2]))
            # context.object.scale = Vector((0.2, 0.2, 0.2))

            bpy.data.objects.remove(bpy.data.objects[self.obj_name])
            bpy.data.objects.remove(bpy.data.objects[self.collider_name])

            PlanGeneratorModalOperator.isRunning = False
            return {'FINISHED'}
        
        if event.type == 'TIMER':
            area_location = bpy.data.objects[self.obj_name].location.copy()
            area_scale = bpy.data.objects[self.obj_name].scale.copy()
            area_dim = bpy.data.objects[self.obj_name].dimensions.copy()
            
            TOL = bpy.context.scene.TOL
            if (area_location-self.last_loc).length > TOL or (area_dim-self.last_dim).length > TOL:
                self.move_margin(area_location, area_scale, area_dim)
                overlap_list = self._check_overlap(bpy.data.objects[self.collider_name])

                obj = bpy.data.objects[self.obj_name]
                if len(overlap_list) > 0:
                    self._change_color(obj)
                    self.isColliding = True
                else:
                    self._set_original_color(obj)
                    self.isColliding = False
        
        return {'PASS_THROUGH'}

    def execute(self, context):
        
        if self.new_plan_name in sceneModel.PlanCollection():
            self.report({'ERROR'}, f"{self.new_plan_name} already exists")

            #logger = logging.getLogger("myblenderlog")
            #logger.info(f"Given plan name is in use")

            PlanGeneratorModalOperator.isRunning = False

            return {'FINISHED'}

        if self.new_plan_name == "":
            self.report({'ERROR'}, f"Empty plan name")

            #logger = logging.getLogger("myblenderlog")
            #logger.info(f"Given plan name is empty")

            PlanGeneratorModalOperator.isRunning = False

            return {'FINISHED'}

        self.create_area(context)

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)

        PlanGeneratorModalOperator.isRunning = True

        return {'RUNNING_MODAL'}

    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

