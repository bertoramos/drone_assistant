
import bpy
import bmesh
from mathutils.bvhtree import BVHTree

"""
Check a mesh overlap other mesh
"""
def check_overlap(bm1, bm2):
    """
    Input:
        - bm1 : bmesh 1st object
        - bm2 : bmesh 2nd object
    returns:
        - True if bm1 overlap bm2
    """

    # Check overlap
    bool_res = True
    bvh1 = BVHTree.FromBMesh(bm1)
    bvh2 = BVHTree.FromBMesh(bm2)
    res = bvh1.overlap(bvh2)

    del bvh1
    del bvh2

    return len(res) != 0
