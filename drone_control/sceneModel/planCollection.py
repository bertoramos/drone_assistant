
from drone_control.patternModel.singletonModel import Singleton
from .planModel import PlanModel

class PlanCollection(metaclass=Singleton):

    def __init__(self):
        self.__planDict = {}
        self.__activePlanID = None

    def getActive(self):
        return self.getPlan(self.__activePlanID)

    def setActive(self, planID: str):
        if planID in self.__planDict:
            self.__activePlanID = planID
        else:
            raise Exception(f"{planID} does not exist")

    def unsetActive(self):
        self.__activePlanID = None

    def addPlan(self, plan: PlanModel):
        self.__planDict[plan.planID] = plan

    def getPlan(self, planID: int):
        if planID in self.__planDict:
            return self.__planDict[planID]
        return None

    def removePlan(self, planID: int):
        if planID in self.__planDict:
            del self.__planDict[planID]
        if self.__activePlanID == planID:
            self.__activePlanID = None

    def __len__(self):
        return len(self.__planDict)

    def __iter__(self):
        return iter(self.__planDict.values())

    def __contains__(self, planID: str):
        return planID in self.__planDict

    activePlan = property(fget=getActive, fset=setActive)
