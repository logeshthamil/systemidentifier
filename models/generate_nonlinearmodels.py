import sumpf
import nlsp

class HammersteinGroupModel(object):
    """
    A class to generate a Hammerstein Group Model.
    """
    def __init__(self, input_signal=None, nonlinear_functions=None, filter_impulseresponses=None,
                 aliasing_compensation=None, downsampling_position=None):
        """
        @param input_signal: the input signal
        @param nonlinear_functions: the nonlinear functions Eg. [nonlinear_function1, nonlinear_function2, ...]
        @param filter_impulseresponse: the filter impulse responses Eg. [impulse_response1, impulse_response2, ...]
        @param aliasing_compensation: the aliasin compensation technique
        Eg. nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
        @param downsampling_position: the downsampling position, Eg. 1 for downsampling immediately after the nonlinear
        block and 2 for downsampling after the filter processing
        """
        pass

    def GetFilterImpulseResponses(self):
        """
        Get the filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinearFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass

    def SetInput(self, input_signal=None):
        """
        Set the input to the model.
        @param input_signal: the input signal
        """
        pass

    def GetOutput(self):
        """
        Get the output signal of the model.
        @return: the output signal
        """
        pass