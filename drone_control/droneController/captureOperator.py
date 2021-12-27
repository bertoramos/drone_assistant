
import bpy

from drone_control.communication import Buffer, ConnectionHandler

class CaptureModalOperator(bpy.types.Operator):
    bl_idname = "scene.capture_modal_operator"
    bl_label = "Capture Modal Operator"

    _timer = None
    _isCapturing = False

    @classmethod
    def poll(cls, context):
        return not CaptureModalOperator._isCapturing

    def modal(self, context, event):

        if event.type == "TIMER":
            # Fin de captura?
            if ConnectionHandler().receive_end_capture():
                CaptureModalOperator._isCapturing = False

                if context.area is not None:
                    context.area.tag_redraw()
                return {'FINISHED'}
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        wm = context.window_manager
        
        if not ConnectionHandler().connected:
            return {'FINISHED'}
        
        # Enviar inicio de captura
        if ConnectionHandler().send_start_capture(5.0):
            CaptureModalOperator._isCapturing = True

            self._timer = wm.event_timer_add(0.01, window=context.window)
            wm.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        pass
