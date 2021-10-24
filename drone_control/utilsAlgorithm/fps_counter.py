
import bpy
import time

from drone_control.patternModel.singletonModel import Singleton

class FPSCounter(metaclass=Singleton):
    
    SAMPLES = 10

    def __init__(self):

        self._fps_pos_time = 0
        self._fps_pos_count = FPSCounter.SAMPLES
        self._fps_pos_value = 0

        self._fps_rot_time = 0
        self._fps_rot_count = FPSCounter.SAMPLES
        self._fps_rot_value = 0

    def notifyPosition(self):
        if self._fps_pos_count == 0:
            end_time = time.time()
            elapsed_time = end_time - self._fps_pos_time

            self._fps_pos_value = FPSCounter.SAMPLES / elapsed_time

            self._fps_pos_time = 0
            self._fps_pos_count = FPSCounter.SAMPLES

        elif self._fps_pos_count == 10:
            self._fps_pos_time = time.time()
        self._fps_pos_count -= 1
    
    def notifyRotation(self):
        if self._fps_rot_count == 0:
            end_time = time.time()
            elapsed_time = end_time - self._fps_rot_time

            self._fps_rot_value = FPSCounter.SAMPLES / elapsed_time

            self._fps_rot_time = 0
            self._fps_rot_count = FPSCounter.SAMPLES

        elif self._fps_rot_count == 10:
            self._fps_rot_time = time.time()
        self._fps_rot_count -= 1
    
    
    def getPositionFPS(self):
        return self._fps_pos_value
    
    def getRotationFPS(self):
        return self._fps_rot_value