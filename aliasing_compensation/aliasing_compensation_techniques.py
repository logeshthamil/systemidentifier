import sumpf

class AliasingCompensation(object):
    def __init__(self, input_signal=None, maximum_harmonics=None):
        pass

    def SetInput(self):
        pass

    def GetOutput(self):
        pass

    def GetHarmonics(self):
        pass

class UpsamplingAliasingCompensation(AliasingCompensation):

    def __init__(self, input_signal=None, maximum_harmonics=1,
                 resampling_algorithm=sumpf.modules.ResampleSignal.SPECTRUM):
        pass
        # signal processing blocks

class LowpassAliasingCompensation(AliasingCompensation):

    def __init__(self, input_signal=None, maximum_harmonics=1, filter_function=None, attenuation=None):
        pass
        # signal processing blocks