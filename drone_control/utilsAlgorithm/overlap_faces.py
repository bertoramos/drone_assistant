
import bpy
from mathutils import Vector, Matrix
from mathutils.geometry import distance_point_to_plane, intersect_line_line
from bmesh.geometry import intersect_face_point

import math
from math import sin, cos

EPS = lambda context: context.scene.TOL
PI = math.pi

def are_coplanar(f0, f1):
    """
    Check planes are coplanar
    f0 : face0
    f1 : face1
    """
    n0 = f0.normal
    n1 = f1.normal

    angle = n0.angle(n1)

    p0 = f0.verts[0].co
    p1 = f1.verts[0].co
    point_inside = abs(distance_point_to_plane(p0, p1, n0)) < EPS(bpy.context)

    return ( abs(angle) < EPS(bpy.context) or abs(angle - PI) < EPS(bpy.context) ) and point_inside

def point_in_segment(point, line):
    """
    Check if is a point in a segment
    point : Vector
    line : (Vector, Vector)
    """
    dist = lambda p1, p2: (p2-p1).length
    D = dist(line[0], line[1])
    d1 = dist(line[0], point)
    d2 = dist(point, line[1])
    return abs(D - (d1 + d2)) <= EPS(bpy.context)

def segments_intersect(line1, line2):
    """
    Check if two segments intersect
    line1 : (Vector, Vector)
    line2 : (Vector, Vector)
    :returns: True if line1 and line2 intersect
    """
    dist = lambda p0, p1: (p1 - p0).length

    x0, y0 = line1[0], line1[1]
    x1, y1 = line2[0], line2[1]

    res = intersect_line_line(x0, y0, x1, y1)
    if res is not None:
        r0 = res[0]
        r1 = res[1]
        # puntos mas cercanos de en una linea a otra linea deben ser iguales
        if dist(r0, r1) <= EPS(bpy.context):
            # comprobar que el punto de cruce pertenece a ambos segmentos
            if point_in_segment(r0, line1) and point_in_segment(r0, line2):
                return True
    return False

def point_inside_face(face, point):
    """
    face : Face
    point : Vector
    Assume point is in same plane
    """
    reflect = intersect_face_point(face, (point.x, point.y, point.z)) # Point reflects over plane
    any_vertex_equal = any([(v.co.xyz - point).length <= EPS(bpy.context) for v in face.verts]) # Any vertex equals point

    return reflect or any_vertex_equal

def faces_overlap(f0, f1):
    """
    Check if two coplanar faces overlap
    f0 : Face
    f1 : Face
    """
    if not are_coplanar(f0, f1):
        return False

    # Check edges intersect
    for e0 in f0.edges:
        for e1 in f1.edges:
            if segments_intersect((e0.verts[0].co, e0.verts[1].co), (e1.verts[0].co, e1.verts[1].co)):
                return True

    # Check if point inside plane
    for p0 in f0.verts:
        for p1 in f1.verts:
            if point_inside_face(f0, p1.co):
                return True
            if point_inside_face(f1, p0.co):
                return True
    return False


def object_faces_overlap(bm0, bm1):
    for f0 in bm0.faces:
        for f1 in bm1.faces:
            if faces_overlap(f0, f1):
                return True
    return False
