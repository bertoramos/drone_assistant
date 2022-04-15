
import bpy

from drone_control.communication import Buffer, ConnectionHandler

class CaptureModalOperator(bpy.types.Operator):
    bl_idname = "scene.capture_modal_operator"
    bl_label = "Capture Operator"

    _timer = None
    _isCapturing = False

    captureTime: bpy.props.IntProperty(name="Capture time (seconds)", min=1, max=30)

    @classmethod
    def poll(cls, context):
        from drone_control.droneController import PositioningSystemModalOperator
        isRunning = PositioningSystemModalOperator.isRunning
        return not CaptureModalOperator._isCapturing and isRunning

    def modal(self, context, event):
        
        if event.type == "TIMER":
            # Fin de captura?
            if ConnectionHandler().receive_end_capture():
                CaptureModalOperator._isCapturing = False

                if context.area is not None:
                    context.area.tag_redraw()
                
                self.report({'INFO'}, "Capture finished")
                return {'FINISHED'}
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        wm = context.window_manager
        
        print("Capture time : ", self.captureTime)

        if not ConnectionHandler().connected:
            return {'FINISHED'}
        
        # Enviar inicio de captura
        
        if ConnectionHandler().send_start_capture(float(self.captureTime)):
            CaptureModalOperator._isCapturing = True

            self._timer = wm.event_timer_add(0.01, window=context.window)
            wm.modal_handler_add(self)
        
        if context.area is not None:
            context.area.tag_redraw()
        
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        pass
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
