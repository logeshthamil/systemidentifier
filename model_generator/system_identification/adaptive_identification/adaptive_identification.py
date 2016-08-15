from nlsp.model_generator.system_identification.system_identification_approaches import SystemIdentification
import numpy
import copy
import sumpf
import nlsp


class Adaptive(SystemIdentification):
    """
    A class to identify a nonlinear system using adaptation algorithm.
    """

    def __init__(self, system_excitation=None, system_response=None, select_branches=None,
                 multichannel_algorithm=nlsp.common.miso_nlms_multichannel,
                 filter_length=2 ** 10, initial_coefficients=None, nonlinear_function=nlsp.nonlinear_function.Power,
                 excitation_length=2 ** 16, excitation_sampling_rate=None, aliasing_compensation=None, iterations=1,
                 step_size=0.1):
        """
        @param system_excitation: the excitation of the nonlinear system
        @param system_response: the response of the nonlinear system
        @param select_branches: the branches of the model to which the filter kernels have to be found Eg. [1,2,3,4,5]
        @param multichannel_algorithm: the multichannel algorithm which is used for system identification
        @param nonlinear_function: the nonlinear functions of the resulting model
        @param excitation_length: the length of the excitation and response signals
        @param excitation_sampling_rate: the sampling rate of the excitation and response signals
        @param aliasing_compensation: the aliasing compensation parameter of the resulting model
        """
        if system_excitation is None:
            self.__system_excitation = sumpf.Signal()
        else:
            self.__system_excitation = system_excitation
        self.multichannel_algorithm = multichannel_algorithm
        self._select_branches = select_branches
        self.__nlfunction = nonlinear_function
        self.__initial_coefficients = initial_coefficients
        self.__filter_length = filter_length
        self.__iterations = iterations
        self.__step_size = step_size
        self.__input_model = nlsp.HammersteinGroupModel
        self._aliasing_compensation = aliasing_compensation
        SystemIdentification.__init__(self, system_response=system_response, select_branches=select_branches,
                                      aliasing_compensation=aliasing_compensation, excitation_length=excitation_length,
                                      excitation_sampling_rate=excitation_sampling_rate)

    def GetExcitation(self):
        """
        Get the excitation signal for system identification.
        @return: the excitation signal
        """
        self._excitation_generator = sumpf.modules.NoiseGenerator(
                distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
                samplingrate=self._sampling_rate, length=self._length, seed="seed")
        return self._excitation_generator.GetSignal()

    def _GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        input_ex = self.GetExcitation()
        outputs = self._system_response
        nonlinear_functions = [self.__nlfunction(degree=i) for i in self._select_branches]
        input_signal = []
        for nonlinear_function in nonlinear_functions:
            aliasing_compensation = self._aliasing_compensation.CreateModified()
            model = nlsp.HammersteinModel(nonlinear_function=nonlinear_function,
                                          aliasing_compensation=aliasing_compensation,
                                          downsampling_position=self._downsampling_position)
            model.SetInput(input_ex)
            input_signal.append(model.GetOutput().GetChannels()[0])
        desired_signal = outputs.GetChannels()[0]
        if self.__initial_coefficients is None:
            w = numpy.zeros((len(input_signal), self.__filter_length))
        else:
            w = []
            for k in self.__initial_coefficients:
                w.append(numpy.asarray(k.GetChannels()[0]))
        kernel = []
        for i in range(self.__iterations):
            w = self.multichannel_algorithm(input_signals_array=input_signal, desired_output=desired_signal,
                                            filter_length=self.__filter_length,
                                            step_size=self.__step_size, initCoeffs=w)
            kernel = []
            for k in w:
                iden_filter = sumpf.Signal(channels=(k,), samplingrate=outputs.GetSamplingRate(), labels=("filter",))
                kernel.append(iden_filter)
        return kernel

    def _GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        nonlinear_functions = []
        for branch in self._select_branches:
            nonlinear_func = self.__nlfunction(degree=branch)
            nonlinear_functions.append(nonlinear_func)
        return nonlinear_functions
