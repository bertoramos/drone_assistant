
import bpy

# begin local import: Change to from . import MODULE
# end local import: Change to from . import MODULE

keymaps = []

def autoregister():
    bpy.utils.register_class(ShowAnnotationPanel)

    # keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new("measureit.runopengl", type='N', value='PRESS', ctrl=True, alt=True)
        keymaps.append((km, kmi))

def autounregister():
    bpy.utils.unregister_class(ShowAnnotationPanel)

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()


class ShowAnnotationPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_ShowAnnotation"
    bl_label = "View"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Options" # Add new tab to N-Panel

    def draw(self, context):
        box = self.layout.box()
        row = box.row()
        if context.window_manager.measureit_run_opengl is False:
            icon = 'PLAY'
            txt = 'Show'
        else:
            icon = "PAUSE"
            txt = 'Hide'
        row.operator("measureit.runopengl", icon=icon, text=txt)
        row.prop(context.scene, "measureit_gl_ghost", text="", icon='GHOST_ENABLED')
        #self.layout.operator("mesh.add_beacon", icon='LIGHT_POINT', text="Create beacon")
