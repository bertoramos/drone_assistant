
import bpy
import time

from drone_control.patternModel.singletonModel import Singleton

class FPSCounter(metaclass=Singleton):
    
    #SAMPLES = 10
    SAMPLE_TIME = 1

    def __init__(self):

        self._fps_pos_time = 0
        self._fps_pos_count = -1 #FPSCounter.SAMPLES
        self._fps_pos_value = 0

        #self._fps_rot_time = 0
        #self._fps_rot_count = FPSCounter.SAMPLES
        #self._fps_rot_value = 0

    def notifyPositionChange(self):
        #if self._fps_pos_count == 0:
        #    end_time = time.time()
        #    elapsed_time = end_time - self._fps_pos_time
        #
        #    print(f"FPS {elapsed_time}")
        #    #self._fps_pos_value = FPSCounter.SAMPLES / elapsed_time
        #
        #    self._fps_pos_time = time.time()
        #    self._fps_pos_count = FPSCounter.SAMPLES
        #
        #    #print(f"FPS {self._fps_pos_value}")
        #
        #elif self._fps_pos_count == 10:
        #    self._fps_pos_time = time.time()
        #self._fps_pos_count -= 1
        if self._fps_pos_count == -1:
            # inicia cuenta
            self._fps_pos_count = 0
            self._fps_pos_time = time.time()
        else:
            elapsed_time = abs(time.time() - self._fps_pos_time)
            if elapsed_time >= FPSCounter.SAMPLE_TIME:
                # calcula fps
                self._fps_pos_value = self._fps_pos_count / elapsed_time
                
                print(self._fps_pos_value, self._fps_pos_count, elapsed_time)

                self._fps_pos_count = -1
            else:
                # cuenta frame
                self._fps_pos_count += 1
    
    def notifyRotationChange(self):
        #if self._fps_rot_count == 0:
        #    end_time = time.time()
        #    elapsed_time = end_time - self._fps_rot_time
#
        #    self._fps_rot_value = FPSCounter.SAMPLES / elapsed_time
#
        #    self._fps_rot_time = time.time()
        #    self._fps_rot_count = FPSCounter.SAMPLES
#
        #    # self.__update()
#
        #elif self._fps_rot_count == 10:
        #    self._fps_rot_time = time.time()
        #self._fps_rot_count -= 1
        pass
    
    def getPositionFPS(self):
        return self._fps_pos_value
    
    def getRotationFPS(self):
        # return self._fps_rot_value
        return 0

