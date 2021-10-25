
import bpy
import time

from drone_control.patternModel.singletonModel import Singleton

class FPSCounter(metaclass=Singleton):
    
    #SAMPLES = 10
    SAMPLE_TIME = 2.0

    def __init__(self):

        self._fps_pos_time = 0
        self._fps_pos_count = -1 #FPSCounter.SAMPLES
        self._fps_pos_value = 0

        self._fps_rot_time = 0
        self._fps_rot_count = -1
        self._fps_rot_value = 0

        self._fps_render_time = 0
        self._fps_render_count = -1
        self._fps_render_value = 0

    def notifyPositionChange(self):
        if self._fps_pos_count == -1:
            # inicia cuenta
            self._fps_pos_count = 1
            self._fps_pos_time = time.time()
        else:
            elapsed_time = abs(time.time() - self._fps_pos_time)
            if elapsed_time >= FPSCounter.SAMPLE_TIME:
                # calcula fps
                self._fps_pos_value = self._fps_pos_count / elapsed_time
                
                print("FPS POSITION: ", self._fps_pos_value, self._fps_pos_count, elapsed_time)

                self._fps_pos_count = -1
            else:
                # cuenta frame
                self._fps_pos_count += 1
    
    def notifyRotationChange(self):
        if self._fps_rot_count == -1:
            # inicia cuenta
            self._fps_rot_count = 1
            self._fps_rot_time = time.time()
        else:
            elapsed_time = abs(time.time() - self._fps_rot_time)
            if elapsed_time >= FPSCounter.SAMPLE_TIME:
                # calcula fps
                self._fps_rot_value = self._fps_rot_count / elapsed_time
                
                print("FPS ROTATION: ", self._fps_rot_value, self._fps_rot_count, elapsed_time)

                self._fps_rot_count = -1
            else:
                # cuenta frame
                self._fps_rot_count += 1
    
    def notifyRender(self):
        if self._fps_render_count == -1:
            self._fps_render_count = 1
            self._fps_render_time = time.time()
        else:
            elapsed_time = abs(time.time() - self._fps_render_time)
            if elapsed_time >= FPSCounter.SAMPLE_TIME:
                self._fps_render_value = self._fps_render_count / elapsed_time

                print("FPS RENDER: ", self._fps_render_value, self._fps_render_count, elapsed_time)

                self._fps_render_count = -1
            else:
                self._fps_render_count += 1
    
    def getPositionFPS(self):
        return self._fps_pos_value
    
    def getRotationFPS(self):
        return self._fps_rot_value
    
    def getRenderFPS(self):
        return self._fps_render_value

