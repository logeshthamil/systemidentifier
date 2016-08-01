import sumpf
import nlsp

class ModifyModel(object):

    def __init__(self, input_model=None, filter_impulseresponse=None, nonlinear_function=None,
                 aliasing_compensation=None):
        pass

    def SetModel(self):
        pass

    def GetModel(self):
        pass

    def SetFilterIR(self):
        pass

    def SetNonlinearFunction(self):
        pass

    def SetAliasingCompensation(self):
        pass

class PredefinedModelGeneration(ModifyModel):

    @staticmethod
    def distortion_box():
        return PredefinedModelGeneration(predefined_model=None)

    def __init__(self, predefined_model=None):
        pass