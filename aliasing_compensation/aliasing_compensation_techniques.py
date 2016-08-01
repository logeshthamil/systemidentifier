import sumpf

class AliasingCompensation(object):
    def __init__(self, input_signal=None, maximum_harmonics=None):
        pass

    def SetMaximumHarmonics(self):
        pass

    def SetPreprocessingInput(self):
        pass

    def GetPreprocessingOutput(self):
        pass

    def SetPostprocessingInput(self):
        pass

    def GetPostprocessingOutput(self):
        pass

class FullUpsamplingAliasingCompensation(AliasingCompensation):

    def __init__(self, input_signal=None, maximum_harmonics=1,
                 resampling_algorithm=sumpf.modules.ResampleSignal.SPECTRUM):
        pass
        # signal processing blocks

class ReducedUpsamplingAliasingCompensation(AliasingCompensation):

    def __init__(self, input_signal=None, maximum_harmonics=1,
                 resampling_algorithm=sumpf.modules.ResampleSignal.SPECTRUM):
        pass
        # signal processing blocks

class LowpassAliasingCompensation(AliasingCompensation):

    def __init__(self, input_signal=None, maximum_harmonics=1, filter_function=None, attenuation=None):
        pass
        # signal processing blocks

class NoAliasingCompensation(AliasingCompensation):

    def __init__(self, input_signal=None, maximum_harmonics=1, filter_function=None, attenuation=None):
        pass