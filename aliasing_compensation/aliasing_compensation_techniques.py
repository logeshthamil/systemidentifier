
class AliasingCompensation(object):
    """
    An abstract base class for aliasing compensation techniques. The aliasing compensation consists of preprocessing and
    postprocessing units. Every derived aliasing compensation technique should implement the signal processing chain for
    aliasing compensation.
    """

    def SetMaximumHarmonics(self, maximum_harmonics=None):
        """
        Sets the maximum harmonics until which the aliasing compensation has to be compensated for.
        @param maximum_harmonics: the maximum harmonics introduced by the nonlinear model
        """
        pass

    def SetPreprocessingInput(self, preprocessing_input=None):
        """
        Sets the input signal of the preprocessing unit.
        @param input_signal: the input signal of the preprocessing unit
        """
        pass

    def GetPreprocessingOutput(self):
        """
        Gets the output signal of the preprocessing aliasing compensation.
        @return: the output signal of the preprocessing aliasing compensation
        """
        pass

    def SetPostprocessingInput(self, postprocessing_input=None):
        """
        Sets the input signal of the postprocessing aliasing compensation.
        @param postprocessing_input: the input signal of the postprocessing aliasing compensation
        """
        pass

    def GetPostprocessingOutput(self):
        """
        Gets the output signal of the postprocessing aliasing compensation.
        @return: the output signal of the postprocessing aliasing compensation
        """
        pass

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
        pass
        # signal processing blocks

    def GetPreprocessingOutput(self):
        """
        Gets the output signal of the preprocessing aliasing compensation.
        @return: the output signal of the preprocessing aliasing compensation
        """
        pass

    def GetPostprocessingOutput(self):
        """
        Gets the output signal of the postprocessing aliasing compensation.
        @return: the output signal of the postprocessing aliasing compensation
        """
        pass

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
        pass
        # signal processing blocks

    def GetPreprocessingOutput(self):
        """
        Gets the output signal of the preprocessing aliasing compensation.
        @return: the output signal of the preprocessing aliasing compensation
        """
        pass

    def GetPostprocessingOutput(self):
        """
        Gets the output signal of the postprocessing aliasing compensation.
        @return: the output signal of the postprocessing aliasing compensation
        """
        pass

class LowpassAliasingCompensation(AliasingCompensation):
    """
    A class to compensate the aliasing introduced in a nonlinear model using a lowpass filter. The cutoff frequency of
    the lowpass filter is modified based on the attenuation needed at the stop band frequency.
    """
    def __init__(self, input_signal=None, maximum_harmonics=1, filter_function=None, attenuation=None):
        """
        @param input_signal: the input signal
        @param maximum_harmonics: the maximum harmonics introduced by the nonlinear model
        @param filter_function: the filter function which can be chosen based on the choice of filter used for aliasing
        compensation Eg. sumpf.modules.FilterGenerator.BUTTERWORTH()
        @param attenuation: the required attenuation (in dB) at the cutoff frequency
        """
        pass
        # signal processing blocks

    def GetPreprocessingOutput(self):
        """
        Gets the output signal of the preprocessing aliasing compensation.
        @return: the output signal of the preprocessing aliasing compensation
        """
        pass

class NoAliasingCompensation(AliasingCompensation):
    """
    A class which acts as a pass through of signals.
    """
    def __init__(self, input_signal=None, maximum_harmonics=1):
        """
        @param input_signal: the input signal
        @param maximum_harmonics: the maximum harmonics introduced by the nonlinear model
        """
        pass

    def GetPreprocessingOutput(self):
        """
        Gets the output signal of the preprocessing aliasing compensation.
        @return: the output signal of the preprocessing aliasing compensation
        """
        pass