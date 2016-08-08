from nlsp.model_generator.model_generator import HGMModelGenerator
import sumpf
import nlsp

class SystemIdentification(HGMModelGenerator):
    """
    A derived class of the ModelGenerator class and an abstract base class of all the system identification algorithms.
    """
    def __init__(self, system_response=None, select_branches=None, length=2**16, sampling_rate=None, aliasing_compensation=None):
        """
        @param system_response: the response of the nonlinear system
        @param select_branches: the branches of the model to which the filter kernels have to be found Eg. [1,2,3,4,5]
        @param length: the length of the excitation and response signals
        @param sampling_rate: the sampling rate of the excitation and response signals
        """
        if system_response is None:
            self._system_response = sumpf.Signal()
        else:
            self._system_response = system_response
        if select_branches is None:
            self._select_branches = [1,2,3,4,5]
        else:
            self._select_branches = select_branches
        self._length = length
        if sampling_rate is None:
            self._sampling_rate = 48000
        else:
            self._sampling_rate = sampling_rate
        if aliasing_compensation is None:
            self._aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=2)
        else:
            self._aliasing_compensation = aliasing_compensation
        self._input_model = nlsp.HammersteinGroupModel()

    def GetExcitation(self):
        """
        This method should be overridden in the derived classes. Get the excitation signal for system identification.
        @return: the excitation signal
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @sumpf.Input(sumpf.Signal)
    def SetResponse(self, response=None):
        """
        Set the response of the nonlinear system.
        @param response: the response
        """
        self._system_response = response
        self._filter_impulseresponses = self.GetFilterImpuleResponses()
        self._nonlinear_functions = self.GetNonlinerFunctions()

    def GetFilterImpuleResponses(self):
        """
        This method should be overridden in the derived classes. Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetNonlinerFunctions(self):
        """
        This method should be overridden in the derived classes. Get the nonlinear functions.
        @return: the nonlinear functions
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @sumpf.Input(tuple,["GetFilterImpulseResponses","GetNonlinearFunctions"])
    def SelectBranches(self, branches=None):
        """
        Set the branches of the model to which the filter kernels have to be found.
        @return: the branches
        """
        self._select_branches = branches