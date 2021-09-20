
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def points_inside(points, bm):
    """
    Question : https://blender.stackexchange.com/questions/31693/how-to-find-if-a-point-is-inside-a-mesh
    Answer : https://blender.stackexchange.com/a/80781
    input:
        points
        - a list of vectors (can also be tuples/lists)
        bm
        - a manifold bmesh with verts and (edge/faces) for which the
          normals are calculated already. (add bm.normal_update() otherwise)
    returns:
        a list
        - a mask lists with True if the point is inside the bmesh, False otherwise
    """
    rpoints = []
    addp = rpoints.append
    bvh = BVHTree.FromBMesh(bm, epsilon=0.0001)

    # return points on polygons
    for point in points:
        fco, normal, _, _ = bvh.find_nearest(point)
        # calcula vector
        #p2 = fco - Vector(point)
        p2 = Vector(point) - fco
        # Si el producto escalar es negativo, "están en direccion opuesta"
        v = p2.dot(normal)
        addp(v < 0.0)  # addp(v >= 0.0) ?

    return rpoints

def is_inside(bm1, bm2):
    """
    input:
        bm1
        - bmesh 1st object
        bm2
        - bmesh 2nd object
    returns:
        if any vertex of bm2 is inside bm1
    """
    # Check inside
    vertex_tmp2 = [vertex.co for vertex in bm2.verts]
    bool_res = points_inside(vertex_tmp2, bm1)
    return any(bool_res)
