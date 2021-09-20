
from .simple_overlap import check_overlap as simple_overlap_check
from .overlap_faces import object_faces_overlap
from .object_inside import is_inside

def check_overlap(bm0, bm1):
    if simple_overlap_check(bm0, bm1):
        #print("Overlap")
        return True
    if object_faces_overlap(bm0, bm1):
        #print("Faces overlap")
        return True
    if is_inside(bm0, bm1):
        #print("Is inside")
        return True
    if is_inside(bm1, bm0):
        #print("Is inside")
        return True
    return False
