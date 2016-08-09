from nlsp.model_generator.model_generator import HGMModelGenerator
import sumpf
import nlsp

class SystemIdentification(HGMModelGenerator):
    """
    A derived class of the ModelGenerator class and an abstract base class of all the system identification algorithms.
    """
    def __init__(self, system_response=None, select_branches=None, aliasing_compensation=None, excitation_length=2 ** 16,
                 excitation_sampling_rate=None):
        """
        @param system_response: the response of the nonlinear system
        @param select_branches: the branches of the model to which the filter kernels have to be found Eg. [1,2,3,4,5]
        @param aliasing_compensation: the aliasing compensation parameter of the resulting model
        @param excitation_length: the length of the excitation and response signals
        @param excitation_sampling_rate: the sampling rate of the excitation and response signals
        """
        # TODO: why do you use only one underscore at the start of the attribute name?
        #    Make private attributes private, by using two underscores.
        #    One underscore indicates, that an attribute is "protected", which
        #    means, that it is not part of the official API, but it can still be
        #    accessed from outside the class. This encurages bad code, that depends
        #    on internal implementation details of the class.
        if system_response is None:
            self._system_response = sumpf.Signal()
        else:
            self._system_response = system_response
        if select_branches is None:
            self._select_branches = [1, 2, 3, 4, 5]
        else:
            self._select_branches = select_branches
        self._length = excitation_length
        if excitation_sampling_rate is None:
            self._sampling_rate = 48000 # TODO: do not hardcode values like the sampling rate. I suggest, you use SuMPF's config feature for this
        else:
            self._sampling_rate = excitation_sampling_rate
        if aliasing_compensation is None:
            self._aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=1)
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

    @sumpf.Input(tuple, ["GetFilterImpulseResponses", "GetNonlinearFunctions"])
    def SelectBranches(self, branches=None):
        """
        Set the branches of the model to which the filter kernels have to be found.
        @return: the branches
        """
        self._select_branches = branches
