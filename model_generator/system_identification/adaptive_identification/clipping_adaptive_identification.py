from nlsp.model_generator.system_identification.system_identification_approaches import SystemIdentification
import sumpf
import nlsp


class ClippingAdaptive(SystemIdentification):
    """
    A class to identify a nonlinear system using adaptation algorithm.
    """

    def __init__(self, system_excitation=None, system_response=None, select_branches=None,
                 multichannel_algorithm=None, nonlinear_function=nlsp.nonlinear_function.HardClip,
                 excitation_length=2 ** 16, excitation_sampling_rate=None, aliasing_compensation=None,
                 thresholds=None):
        """
        :param system_excitation: the excitation of the nonlinear system
        :param system_response: the response of the nonlinear system
        :param select_branches: the branches of the model to which the filter kernels have to be found Eg. [1,2,3,4,5]
        :param multichannel_algorithm: the multichannel algorithm which is used for system identification
        :param nonlinear_function: the nonlinear functions of the resulting model
        :param excitation_length: the length of the excitation and response signals
        :param excitation_sampling_rate: the sampling rate of the excitation and response signals
        :param aliasing_compensation: the aliasing compensation parameter of the resulting model
        """
        if system_excitation is None:
            self.__system_excitation = sumpf.Signal()
        else:
            self.__system_excitation = system_excitation
        if multichannel_algorithm is None:
            self.multichannel_algorithm = nlsp.MISO_NLMS_algorithm()
        else:
            self.multichannel_algorithm = multichannel_algorithm
        if select_branches is None:
            self._select_branches = range(1, len(thresholds) + 1)
        else:
            self._select_branches = select_branches
        self.__nlfunction = nonlinear_function
        self.__input_model = nlsp.HammersteinGroupModel
        self._aliasing_compensation = aliasing_compensation
        if thresholds is None:
            self.__thresholds = [[-1.0, 1.0], ] * max(self._select_branches)
        else:
            self.__thresholds = thresholds
        SystemIdentification.__init__(self, system_response=system_response, select_branches=self._select_branches,
                                      aliasing_compensation=self._aliasing_compensation,
                                      excitation_length=excitation_length,
                                      excitation_sampling_rate=excitation_sampling_rate)

    def GetExcitation(self, excitation_length=None, excitation_sampling_rate=None):
        """
        Get the excitation signal for system identification.

        :param excitation_length: the length of the excitation signal
        :param excitation_sampling_rate: the sampling rate of the excitation signal
        :return: the excitation signal
        """
        if excitation_length is not None:
            self._length = excitation_length
        if excitation_sampling_rate is not None:
            self._sampling_rate = excitation_sampling_rate
        self._excitation_generator = sumpf.modules.NoiseGenerator(
            distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
            samplingrate=self._sampling_rate, length=self._length, seed="seed")
        return self._excitation_generator.GetSignal()

    def _GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.

        :return: the filter impulse responses
        """
        input_ex = self.GetExcitation()
        nonlinear_functions = self._GetNonlinerFunctions()
        input_signal = sumpf.modules.MergeSignals()
        for nonlinear_function in nonlinear_functions:
            aliasing_compensation = self._aliasing_compensation.CreateModified()
            model = nlsp.HammersteinModel(nonlinear_function=nonlinear_function,
                                          aliasing_compensation=aliasing_compensation,
                                          downsampling_position=self._downsampling_position)
            model.SetInput(input_ex)
            input_signal.AddInput(model.GetOutput())
        input_signal = input_signal.GetOutput()
        desired_signal = self._system_response
        self.multichannel_algorithm.SetInput(input_signal=input_signal)
        self.multichannel_algorithm.SetDesiredOutput(desired_output=desired_signal)
        w = self.multichannel_algorithm.GetFilterKernel()
        kernel = [sumpf.modules.SplitSignal(data=w, channels=[i]).GetOutput() for i in range(len(w.GetChannels()))]
        if self._filter_length is not None:
            filter_kernels = []
            for k in kernel:
                filter_kernels.append(
                    nlsp.common.helper_functions_private.change_length_signal(signal=k, length=self._filter_length))
        else:
            filter_kernels = kernel
        return filter_kernels

    def _GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.

        :return: the nonlinear functions
        """
        self.__nlfunction = nlsp.nonlinear_function.HardClip
        nonlinear_functions = []
        for branch in self._select_branches:
            nonlinear_func = self.__nlfunction(clipping_threshold=self.__thresholds[branch - 1])
            nonlinear_functions.append(nonlinear_func)
        return nonlinear_functions
