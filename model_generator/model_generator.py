import nlsp
import sumpf

class ModelGenerator():
    def __init__(self):
        pass

    def GetOutputModel(self):
        pass

class ModifyModel(ModelGenerator):

    def __init__(self, input_model=None, filter_impulseresponse=None, nonlinear_function=None,
                 aliasing_compensation=None):
        pass

    def SetInputModel(self):
        pass

    def SetFilterImpulseResponses(self):
        pass

    def SetNonlinearFunctions(self):
        pass

    def SetAliasingCompensation(self):
        pass


class PredefinedModelGeneration(object):

    @staticmethod
    def distortion_box():
        return PredefinedModelGeneration(predefined_model=None)

    def __init__(self, predefined_model=None, number_of_branches=None):
        pass

    def SelectPredefinedModel(self):
        pass

    def SetNumberofBranches(self):
        pass
