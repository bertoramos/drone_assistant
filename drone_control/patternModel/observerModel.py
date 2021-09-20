
from abc import ABC, abstractmethod

class Observer(ABC):

    @abstractmethod
    def notify(self):
        pass

class Notifier(ABC):

    @abstractmethod
    def attach(self, observer: Observer):
        pass

    @abstractmethod
    def detach(self, observer: Observer):
        pass

    @abstractmethod
    def notifyAll(self):
        pass
