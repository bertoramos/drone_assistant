
import threading

class StoppableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stopper = threading.Event()
    
    def stop(self):
        self._stopper.set()
    
    def stopped(self):
        return self._stopper.isSet()
