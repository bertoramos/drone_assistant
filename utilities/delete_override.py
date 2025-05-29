import bpy
from bpy.props import BoolProperty

# begin local import: Change to from . import MODULE
import RobomapKeymap
# end local import: Change to from . import MODULE

def autoregister():
    bpy.utils.register_class(DeleteOverrideOperator)
    RobomapKeymap.load_keymap()
    bpy.context.preferences.keymap.active_keyconfig="RobomapKeymap"
    

def autounregister():
    bpy.utils.unregister_class(DeleteOverrideOperator)

"""
Overrides Delete Operator
Avoid delete protected objects
"""
bpy.types.Object.protected = BoolProperty(name = 'protected', default = False)


def drop(obj):
    obj_name = obj.name
    mesh = obj.data
    material = obj.active_material

    # Eliminamos objeto
    if obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)

    # Eliminamos el mesh que lo forma
    if mesh is not None:
        mesh_name = mesh.name
        if mesh_name in bpy.data.meshes:
            bpy.data.meshes.remove(bpy.data.meshes[mesh_name], do_unlink=True)
        if mesh_name in bpy.data.lights:
            bpy.data.lights.remove(bpy.data.lights[mesh_name], do_unlink=True)

    # Eliminamos su material
    if material is not None:
        material_name = material.name
        if material_name in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials[material_name], do_unlink=True)
    # bpy.ops.select_all
    bpy.ops.object.select_all(action='DESELECT')

def get_children(parent):
    not_visited = [parent]
    children = []
    while len(not_visited) > 0:
        current_node = not_visited.pop(0)
        children.extend(current_node.children)
        not_visited.extend(current_node.children)
    return children

def delete(self, context, delete_children=False):
    protected_obj = []
    to_delete = [obj for obj in context.selected_objects] # map deleted objects : avoid an invalid object error when the child of a selected object is also selected
    for obj in to_delete:
        if not obj.protected:
            if delete_children:
                children = get_children(obj)
                for child in children:
                    if child in to_delete: # indicates selected child was deleted
                        to_delete.remove(child)
                    drop(child)
            drop(obj)
        else :
            protected_obj.append(obj.name)
    if len(protected_obj) == 1:
        self.report({'ERROR'}, (protected_obj[0] +' is protected'))
    elif len(protected_obj) > 1:
        self.report({'ERROR'}, (str(protected_obj)[1:-1] +' are protected'))

class DeleteOverrideOperator(bpy.types.Operator):
    """delete unprotected objects"""
    bl_idname = "object.custom_delete"
    bl_label = "Delete unprotected"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_description = "Delete selected objects and optionally children"

    delete_children: BoolProperty(default=True)
    use_global: BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        delete(self, context, self.delete_children)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "delete_children", text="Recursively delete")
