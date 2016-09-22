from nlsp.model_generator.system_identification.system_identification_approaches import SystemIdentification
import sumpf
import nlsp
import pandas


class ClippingAdaptiveIIR(SystemIdentification):
    """
    A class to identify a nonlinear system using adaptation algorithm.
    """

    def __init__(self, system_excitation=None, system_response=None, select_branches=None,
                 multichannel_algorithm=None, nonlinear_function=nlsp.nonlinear_function.HardClip,
                 excitation_length=2 ** 16, excitation_sampling_rate=None, aliasing_compensation=None,
                 thresholds=None, initial_coefficients=None, filter_order=8, algorithm='Powell',
                 start_frequency=50.0, stop_frequency=19000.0, printeachiteration=False, plotindividual=False,
                 maxiterations=50):
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

        # curve tracing parameters
        self.__initialcoeff = initial_coefficients
        self.__algorithm = algorithm
        self.__filter_order = filter_order
        self.__startfreq = start_frequency
        self.__stopfreq = stop_frequency
        self.__printeachiteration = printeachiteration
        self.__plotindividual = plotindividual
        self.__maxiterations = maxiterations


        SystemIdentification.__init__(self, system_response=system_response, select_branches=self._select_branches,
                                      aliasing_compensation=self._aliasing_compensation,
                                      excitation_length=excitation_length,
                                      excitation_sampling_rate=excitation_sampling_rate)
        self.__coefficients = None
        if (self.__system_excitation is not None) and (self._system_response is not None):
            self.SetResponse(self._system_response)

    @sumpf.Output(sumpf.Signal)
    def GetExcitation(self, excitation_length=None, excitation_sampling_rate=None):
        """
        Get the excitation signal for system identification.

        :param excitation_length: the length of the excitation signal
        :param excitation_sampling_rate: the sampling rate of the excitation signal
        :return: the excitation signal
        """
        if self.__system_excitation is None:
            if excitation_length is not None:
                self._length = excitation_length
            if excitation_sampling_rate is not None:
                self._sampling_rate = excitation_sampling_rate
            excitation_generator = sumpf.modules.NoiseGenerator(
                distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
                samplingrate=self._sampling_rate, length=self._length, seed="seed")
            self.__system_excitation = excitation_generator.GetSignal()
        return self.__system_excitation

    @sumpf.Input(sumpf.Signal, ["GetExcitation", "_GetFilterImpuleResponses", "_GetNonlinerFunctions"])
    def _SetExcitation(self, excitation):
        self.__system_excitation = excitation

    @sumpf.Output(tuple)
    def _GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.

        :return: the filter impulse responses
        """
        algorithm = nlsp.system_identification.ClippingAdaptive(system_excitation=self.__system_excitation, system_response=self._system_response,
                                                                select_branches=self._select_branches, multichannel_algorithm=self.multichannel_algorithm,
                                                                nonlinear_function=self._GetNonlinerFunctions, excitation_length=self._length, excitation_sampling_rate=self._sampling_rate,
                                                                aliasing_compensation=self._aliasing_compensation, thresholds=self.__thresholds)
        output_model = algorithm.GetOutputModel()
        filter_kernels_fir = output_model.GetFilterImpulseResponses()
        filter_kernels, coefficients = nlsp.curve_fitting_algorithms.compute_iir_from_fir_using_curvetracing_higherorder(fir_kernels=filter_kernels_fir, initial_coeff=self.__initialcoeff, filter_order=self.__filter_order,
                                                                                          start_freq=self.__startfreq, stop_freq=self.__stopfreq, Print=self.__printeachiteration, max_iterations=self.__maxiterations,
                                                                                          plot_individual=self.__plotindividual)
        self.__coefficients = coefficients
        return filter_kernels

    @sumpf.Output(tuple)
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

    @sumpf.Output(pandas.Series)
    def GetFilterCoefficients(self):
        if self.__coefficients is None:
            print "The filter coefficients are not yet found!"
            raise
        return self.__coefficients