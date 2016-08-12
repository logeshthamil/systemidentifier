import sumpf
import math

class FindHarmonicImpulseResponse_NovakSweep(object):
    def __init__(self,
                 impulse_response=None,
                 harmonic_order=2,
                 sweep_generator=None):
        if harmonic_order < 2:
            raise ValueError("The harmonic order has to be at least 2.")
        self.__impulse_response = impulse_response
        if impulse_response is None:
            self.__impulse_response = sumpf.modules.ImpulseGenerator().GetSignal()
        self.__harmonic_order = harmonic_order
        self.__sweep_generator = sweep_generator
        self.__sweep_start_frequency = sweep_generator.GetStartFrequency()
        self.__sweep_stop_frequency = sweep_generator.GetStopFrequency()
        self.__sweep_duration = sweep_generator.GetLength() / impulse_response.GetSamplingRate()
        self.__sweep_duration_2 = len(self.__impulse_response) / self.__impulse_response.GetSamplingRate()

    @sumpf.Input(sumpf.Signal, "GetHarmonicImpulseResponse")
    def SetImpulseResponse(self, impulse_response):
        self.__impulse_response = impulse_response

    @sumpf.Input(int, "GetHarmonicImpulseResponse")
    def SetHarmonicOrder(self, order):
        if order < 2:
            raise ValueError("The harmonic order has to be at least 2.")
        self.__harmonic_order = order

    @sumpf.Output(sumpf.Signal)
    def GetHarmonicImpulseResponse(self):
        # stable
        sweep_rate = self.__sweep_generator.GetSweepExcitationRate()
        harmonic_start_time = self.__sweep_duration - (math.log(self.__harmonic_order) * sweep_rate)

        harmonic_start_sample = sumpf.modules.DurationToLength(duration=harmonic_start_time,
                                                               samplingrate=self.__impulse_response.GetSamplingRate(),
                                                               even_length=False).GetLength()
        harmonic_stop_sample = len(self.__impulse_response)
        if self.__harmonic_order > 2:
            harmonic_stop_time = self.__sweep_duration - (math.log(self.__harmonic_order - 1) * sweep_rate)
            harmonic_stop_sample = sumpf.modules.DurationToLength(duration=harmonic_stop_time,
                                                                  samplingrate=self.__impulse_response.GetSamplingRate(),
                                                                  even_length=False).GetLength()
        # prepare the labels
        labels = []
        affix = " (%s harmonic)" % sumpf.helper.counting_number(self.__harmonic_order)
        for l in self.__impulse_response.GetLabels():
            if l is None:
                labels.append("Impulse Response" + affix)
            else:
                labels.append(l + affix)
        # crop to the impulse response of the wanted harmonic
        cropped = self.__impulse_response[harmonic_start_sample:harmonic_stop_sample]
        harmonic = sumpf.Signal(channels=cropped.GetChannels(),
                                samplingrate=cropped.GetSamplingRate() / self.__harmonic_order, labels=tuple(labels))
        if len(harmonic) % 2 != 0:
            harmonic = sumpf.Signal(channels=tuple([c + (0.0,) for c in harmonic.GetChannels()]),
                                    samplingrate=harmonic.GetSamplingRate(), labels=harmonic.GetLabels())
        return harmonic
