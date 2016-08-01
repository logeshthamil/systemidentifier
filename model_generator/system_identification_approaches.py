import sumpf
import nlsp
from .model_generator import ModelGenerator

class SystemIdentification(ModelGenerator):
    def __init__(self):
        pass

    def GetExcitation(self, length=None, sampling_rate=None):
        pass

    def SetResponse(self, response=None):
        pass

    def GetFilterImpuleResponses(self):
        pass

    def GetNonlinerFunctions(self):
        pass

    def SelectBranches(self):
        pass

class SineSweep(SystemIdentification):

    def __init__(self, response=None, branches=5):
        pass

class CosineSweep(SystemIdentification):

    def __init__(self, response=None, branches=5):
        pass

class MISOapproach(SystemIdentification):

    def __init__(self, response=None, branches=5):
        pass

class WienerGapproach(SystemIdentification):

    def __init__(self, response=None, branches=5):
        pass

class Adaptive(SystemIdentification):

    def __init__(self, excitation=None, response=None, branches=5, algorithm=None, nonlinear_function=None):
        pass