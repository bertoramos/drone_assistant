
import bpy

from drone_control.communication import Buffer, ConnectionHandler

class ToggleCaptureOperator(bpy.types.Operator):
    bl_idname = "scene.toggle_capture"
    bl_label  = "Start capture"

    isCapturing = False

    @classmethod
    def poll(cls, context):
        from drone_control.droneController import PositioningSystemModalOperator
        isRunning = PositioningSystemModalOperator.isRunning
        return isRunning and not TimedCaptureModalOperator._isCapturing
    
    def start_capture(self, context):
        if ConnectionHandler().send_start_capture():
            ToggleCaptureOperator.isCapturing = True

    def stop_capture(self, context):
        if ConnectionHandler().send_stop_capture():
            ToggleCaptureOperator.isCapturing = False
    
    def execute(self, context):
        if not ToggleCaptureOperator.isCapturing:
            self.start_capture(context)
        else:
            self.stop_capture(context)
        
        print("Hello ", ToggleCaptureOperator.isCapturing)
        return {'FINISHED'}


class TimedCaptureModalOperator(bpy.types.Operator):
    bl_idname = "scene.timed_capture_modal_operator"
    bl_label = "Timed Capture Modal Operator"
    
    _timer = None
    _isCapturing = False
    
    captureTime: bpy.props.IntProperty(name="Capture time (seconds)", min=1, max=30, default=5)
    
    @classmethod
    def poll(cls, context):
        from drone_control.droneController import PositioningSystemModalOperator
        isRunning = PositioningSystemModalOperator.isRunning
        return not TimedCaptureModalOperator._isCapturing and isRunning and not ToggleCaptureOperator.isCapturing

    def modal(self, context, event):
        # esperar a que finalice captura
        if event.type == "TIMER":
            # Fin de captura?
            if ConnectionHandler().receive_end_timed_capture():
                TimedCaptureModalOperator._isCapturing = False

                if context.area is not None:
                    context.area.tag_redraw()
                
                self.report({'INFO'}, "Capture finished")
                return {'FINISHED'}
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        # iniciar captura y lanzar TIMER
        wm = context.window_manager
        
        if not ConnectionHandler().connected:
            return {'FINISHED'}
        
        if ConnectionHandler().send_start_timed_capture(float(self.captureTime)):
            TimedCaptureModalOperator._isCapturing = True

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
    
"""
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
"""