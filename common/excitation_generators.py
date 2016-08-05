import numpy
import sumpf

class Sinesweepgenerator_Novak(object):
    """
    A class to generate the sine sweep signal which compensates the phase shift of higher order harmonics.
    """
    def __init__(self, sampling_rate=None, approximate_numberofsamples=2**16, start_frequency=20.0,
                 stop_frequency=20000.0, fade_out=0.02, fade_in=0.02, amplitude_range=1.0):
        """
        @param sampling_rate: the sampling rate
        @param approximate_length: the approximate number of samples of the sweep signal,
        the length of the output signal will be different
        @param start_frequency: the start frequency
        @param stop_frequency: the stop frequency
        @param fade_out: the fade out length in seconds
        @param fade_in: the fade in length in seconds
        @param factor: the amplitude range of the sweep signal
        """
        if sampling_rate is None:
            self.__sampling_rate = 48000
        else:
            self.__sampling_rate = float(sampling_rate)
        self.__approx_length = float(approximate_numberofsamples)
        self.__start_frequency = float(start_frequency)
        self.__stop_frequency = float(stop_frequency)
        self.__fade_out = float(fade_out*self.__sampling_rate)
        self.__fade_in = float(fade_in*self.__sampling_rate)
        self.__excitation_factor = amplitude_range

    @sumpf.Input(float,"GetLength")
    def SetLength(self, approximate_numberofsamples):
        """
        Set the approximate number of samples of the sweep signal.
        @param approximate_length: the approximate number of samples of excitation
        @return:
        """
        self.__approx_length = float(approximate_numberofsamples)

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Get the output sine sweep signal.
        @return: the output sine sweep signal
        """
        t = numpy.arange(0,self.GetLength()/self.__sampling_rate,1/self.__sampling_rate)
        s = numpy.sin(2*numpy.pi*self.__start_frequency*self.GetSweepExcitationRate()*(numpy.exp(t/self.GetSweepExcitationRate())-1))
        if self.__fade_in > 0:
            s[0:self.__fade_in] = s[0:self.__fade_in] * ((-numpy.cos(numpy.arange(self.__fade_in)/self.__fade_in*numpy.pi)+1) / 2)
        if self.__fade_out > 0:
            s[-self.__fade_out:] = s[-self.__fade_out:] *  ((numpy.cos(numpy.arange(self.__fade_out)/self.__fade_out*numpy.pi)+1) / 2)
        signal = sumpf.Signal(channels=(s,),samplingrate=self.__sampling_rate,labels=("Sweep signal",))
        if len(signal) % 2 != 0:
            signal = sumpf.modules.CutSignal(signal,start=0,stop=-1).GetOutput()
        signal = self.GetAmplitudeRange() * signal
        return signal

    @sumpf.Output(sumpf.Signal)
    def GetReversedOutput(self, numberofsamples=None):
        """
        Get the reversed output sine sweep signal.
        @param numberofsamples: number of samples of the reversed sine sweep signal
        @return:
        """
        if numberofsamples is None:
            length = self.GetLength()
        else:
            length = numberofsamples
        sweep_parameter = self.GetSweepExcitationRate()
        # fft_len = int(2**numpy.ceil(numpy.log2(length)))
        fft_len = int(length)
        interval = numpy.linspace(0, self.__sampling_rate/2, num=fft_len/2+1)
        inverse_sweep = 2*numpy.sqrt(interval/sweep_parameter)*numpy.exp(1j*(2*numpy.pi*sweep_parameter*interval*(self.GetStartFrequency()/interval +
                                                                     numpy.log(interval/self.GetStartFrequency()) - 1) + numpy.pi/4))
        inverse_sweep[0] = 0j
        rev_sweep = numpy.fft.irfft(inverse_sweep)
        rev_sweep = sumpf.Signal(channels=(rev_sweep,), samplingrate=self.__sampling_rate,
                                 labels=("Reversed Sweep signal",))
        rev_sweep = (1.0/self.GetAmplitudeRange())*rev_sweep
        return rev_sweep

    @sumpf.Output(float)
    def GetSweepExcitationRate(self):
        """
        Get the sweep excitation rate.
        @return: the sweep excitation rate
        """
        L = 1/self.__start_frequency * round((self.__approx_length/self.__sampling_rate)*
                                             self.__start_frequency/numpy.log(self.__stop_frequency/self.__start_frequency))
        return L

    @sumpf.Output(float)
    def GetLength(self):
        """
        Get the actual length of the sine sweep signal.
        @return: the acutual length
        """
        T_hat = self.GetSweepExcitationRate()*numpy.log(self.__stop_frequency/self.__start_frequency)
        length = round(self.__sampling_rate*T_hat-1)
        return length

    @sumpf.Output(float)
    def GetAmplitudeRange(self):
        """
        Get the amplitude range of the sine sweep signal.
        @return: the amplitude range
        """
        return self.__excitation_factor

    @sumpf.Input(float,["GetAmplitudeRange", "GetOutput", "GetReversedOutput"])
    def SetAmplitudeRange(self, amplitude_range):
        """
        Set the amplitude range of the sine sweep signal.
        @param amplitude_range: the amplitude range
        @return: the amplitude range
        """
        self.__excitation_factor = amplitude_range

    @sumpf.Output(float)
    def GetStartFrequency(self):
        """
        Get the start frequency of the excitation signal.
        @return: the start frequency
        """
        return self.__start_frequency

    @sumpf.Output(float)
    def GetStopFrequency(self):
        """
        Get the stop frequency of the excitation signal.
        @return: the stop frequency
        """
        return self.__stop_frequency