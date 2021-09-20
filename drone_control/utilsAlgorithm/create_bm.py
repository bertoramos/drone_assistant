
import bpy
import bmesh

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
