import sumpf
import nlsp

class GenerateNonlinearModel(object):
    def __init__(self, nonlinear_functions=None, filter_impulseresponses=None, aliasing_compensation=None):
        pass

    def GetFilterImpulseResponses(self):
        pass

    def GetNonlinearFunctions(self):
        pass

    def SetInput(self, signal=None):
        pass

    def GetOutput(self):
        pass

class HammersteinGroupModel(GenerateNonlinearModel):
    def __init__(self, input_signal=None, nonlinear_function=None, filter_impulseresponse=None,
                 aliasing_compensation=None, downsampling_position=None):
        pass