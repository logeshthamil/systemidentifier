import sumpf
import math


class AliasingCompensation(object):
    """
    An abstract base class for aliasing compensation techniques. The aliasing compensation consists of preprocessing and
    postprocessing units. Every derived aliasing compensation technique should implement the signal processing chain for
    aliasing compensation.
    """
    def __init__(self, input_signal=None, maximum_harmonics=None):
        """
        @param input_signal: the input signal
        @param maximum_harmonics: the maximum harmonics introduced by the nonlinear model
        @return:
        """
        if input_signal is None:
            self._input_signal = sumpf.Signal()
        else:
            self._input_signal = input_signal
        if maximum_harmonics is None:
            self._maximum_harmonics = 1
        else:
            self._maximum_harmonics = maximum_harmonics

    @sumpf.Input(data_type=int)
    def SetMaximumHarmonics(self, maximum_harmonics=None):
        """
        Sets the maximum harmonics until which the aliasing compensation has to be compensated for.
        @param maximum_harmonics: the maximum harmonics introduced by the nonlinear model
        """
        self._maximum_harmonics = maximum_harmonics

    @sumpf.Input(data_type=sumpf.Signal, observers=["GetPreprocessingOutput"])
    def SetPreprocessingInput(self, preprocessing_input=None):
        """
        Sets the input signal of the preprocessing unit.
        @param input_signal: the input signal of the preprocessing unit
        """
        self._input_signal = preprocessing_input

    @sumpf.Output(data_type=sumpf.Signal)
    def GetPreprocessingOutput(self):
        """
        Gets the output signal of the preprocessing aliasing compensation.
        @return: the output signal of the preprocessing aliasing compensation
        """
        return self._input_signal

    @sumpf.Input(data_type=sumpf.Signal, observers=["GetPostprocessingOutput"])
    def SetPostprocessingInput(self, postprocessing_input=None):
        """
        Sets the input signal of the postprocessing aliasing compensation.
        @param postprocessing_input: the input signal of the postprocessing aliasing compensation
        """
        self._postprocessing_input = postprocessing_input

    @sumpf.Output(data_type=sumpf.Signal)
    def GetPostprocessingOutput(self):
        """
        Gets the output signal of the postprocessing aliasing compensation.
        @return: the output signal of the postprocessing aliasing compensation
        """
        return self._postprocessing_input

    @sumpf.Output(float)
    def _GetAttenuation(self):
        attenuation = self._input_signal.GetSamplingRate() / self.GetPreprocessingOutput().GetSamplingRate()
        return attenuation


class FullUpsamplingAliasingCompensation(AliasingCompensation):
    """
    A class to compensate the aliasing introduced in a nonlinear model using an upsampler. The upsampling factor of the
    upsampler is chosen such that aliasing is prevented in the whole spectrum of the nonlinearly processed signals.
    """

    def __init__(self, input_signal=None, maximum_harmonics=None, resampling_algorithm=None):
        """
        @param input_signal: the input signal
        @param maximum_harmonics: the maximum harmonics introduced by the nonlinear model
        @param resampling_algorithm: the resampling algorithms Eg. sumpf.modules.ResampleSignal.SPECTRUM()
        """
        AliasingCompensation.__init__(self, input_signal=input_signal, maximum_harmonics=maximum_harmonics)
        if resampling_algorithm is None:
            self._resampling_algorithm = sumpf.modules.ResampleSignal.SPECTRUM
        else:
            self._resampling_algorithm = resampling_algorithm

    def CreateModified(self, input_signal=None, maximum_harmonics=None, resampling_algorithm=None):
        """
        @param input_signal: the input signal
        @param maximum_harmonics: the maximum harmonics introduced by the nonlinear model
        @param resampling_algorithm: the resampling algorithms Eg. sumpf.modules.ResampleSignal.SPECTRUM()
        """
        if input_signal is None:
            input_signal = self._input_signal
        if maximum_harmonics is None:
            maximum_harmonics = self._maximum_harmonics
        return self.__class__(input_signal=input_signal, degree=degree)

    @sumpf.Output(data_type=sumpf.Signal)
    def GetPreprocessingOutput(self):
        """
        Gets the output signal of the preprocessing aliasing compensation.
        @return: the output signal of the preprocessing aliasing compensation
        """
        resampling_rate = self._input_signal.GetSamplingRate() * self._maximum_harmonics
        resampler = sumpf.modules.ResampleSignal(signal=self._input_signal, samplingrate=resampling_rate,
                                                 algorithm=self._resampling_algorithm)
        return resampler.GetOutput()

    @sumpf.Output(data_type=sumpf.Signal)
    def GetPostprocessingOutput(self):
        """
        Gets the output signal of the postprocessing aliasing compensation.
        @return: the output signal of the postprocessing aliasing compensation
        """
        resampling_rate = self._input_signal.GetSamplingRate()
        resampler = sumpf.modules.ResampleSignal(signal=self._postprocessing_input, samplingrate=resampling_rate,
                                                 algorithm=self._resampling_algorithm)
        return resampler.GetOutput()


class ReducedUpsamplingAliasingCompensation(AliasingCompensation):
    """
    A class to compensate the aliasing introduced in a nonlinear model using an upsampler. The upsampling factor of the
    upsampler is chosen such that aliasing is prevented in the baseband spectrum of the input signal.
    """

    def __init__(self, input_signal=None, maximum_harmonics=1, resampling_algorithm=None):
        """
        @param input_signal: the input signal
        @param maximum_harmonics: the maximum harmonics introduced by the nonlinear model
        @param resampling_algorithm: the resampling algorithms Eg. sumpf.modules.ResampleSignal.SPECTRUM()
        """
        AliasingCompensation.__init__(self, input_signal=input_signal, maximum_harmonics=maximum_harmonics)
        if resampling_algorithm is None:
            self._resampling_algorithm = sumpf.modules.ResampleSignal.SPECTRUM
        else:
            self._resampling_algorithm = resampling_algorithm

    @sumpf.Output(data_type=sumpf.Signal)
    def GetPreprocessingOutput(self):
        """
        Gets the output signal of the preprocessing aliasing compensation.
        @return: the output signal of the preprocessing aliasing compensation
        """
        resampling_rate = self._input_signal.GetSamplingRate() * math.ceil((self._maximum_harmonics + 1.0) / 2.0)
        resampler = sumpf.modules.ResampleSignal(signal=self._input_signal, samplingrate=resampling_rate,
                                                 algorithm=self._resampling_algorithm)
        return resampler.GetOutput()

    @sumpf.Output(data_type=sumpf.Signal)
    def GetPostprocessingOutput(self):
        """
        Gets the output signal of the postprocessing aliasing compensation.
        @return: the output signal of the postprocessing aliasing compensation
        """
        resampling_rate = self._input_signal.GetSamplingRate()
        resampler = sumpf.modules.ResampleSignal(signal=self._postprocessing_input, samplingrate=resampling_rate,
                                                 algorithm=self._resampling_algorithm)
        return resampler.GetOutput()


class LowpassAliasingCompensation(AliasingCompensation):
    """
    A class to compensate the aliasing introduced in a nonlinear model using a lowpass filter. The cutoff frequency of
    the lowpass filter is modified based on the attenuation needed at the stop band frequency.
    """

    def __init__(self, input_signal=None, maximum_harmonics=1, filter_function_class=sumpf.modules.FilterGenerator.BUTTERWORTH,
                 filter_order=16, attenuation=60):
        """
        @param input_signal: the input signal
        @param maximum_harmonics: the maximum harmonics introduced by the nonlinear model
        @param filter_function_class: the filter function which can be chosen based on the choice of filter used for
        aliasing compensation Eg. sumpf.modules.FilterGenerator.BUTTERWORTH
        @param attenuation: the required attenuation (in dB) at the stopband frequency of the filter
        """
        AliasingCompensation.__init__(self, input_signal=input_signal, maximum_harmonics=maximum_harmonics)
        self._filter_function = sumpf.modules.FilterGenerator(filterfunction=filter_function_class(order=filter_order))
        self._attenuation = attenuation
        self._filter_order = filter_order

    @sumpf.Output(data_type=sumpf.Signal)
    def GetPreprocessingOutput(self):
        """
        Gets the output signal of the preprocessing aliasing compensation.
        @return: the output signal of the preprocessing aliasing compensation
        """
        property = sumpf.modules.ChannelDataProperties()
        property.SetSignal(signal=self._input_signal)
        cutoff_frequency = ((self._input_signal.GetSamplingRate() / 2.0) / self._maximum_harmonics) \
                           / (2.0 ** (self._attenuation / (6.0 * self._filter_order)))
        self._filter_function.SetFrequency(frequency=cutoff_frequency)
        self._filter_function.SetResolution(property.GetResolution())
        self._filter_function.SetLength(property.GetSpectrumLength())
        result_spectrum = sumpf.modules.Multiply(
            value1=sumpf.modules.FourierTransform(self._input_signal).GetSpectrum(),
            value2=self._filter_function.GetSpectrum()).GetResult()
        return sumpf.modules.InverseFourierTransform(spectrum=result_spectrum).GetSignal()


class NoAliasingCompensation(AliasingCompensation):
    """
    A class which acts as a pass through of signals.
    """

    def __init__(self, input_signal=None, maximum_harmonics=1):
        """
        @param input_signal: the input signal
        @param maximum_harmonics: the maximum harmonics introduced by the nonlinear model
        """
        AliasingCompensation.__init__(self, input_signal=input_signal, maximum_harmonics=maximum_harmonics)
