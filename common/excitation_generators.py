import numpy
import sumpf


class Sinesweepgenerator_Novak(object):
    def __init__(self, sampling_rate=48000.0, length=2**16, start_frequency=20.0,
                 stop_frequency=20000.0, fade_out=0.02, fade_in=0.02, factor=1.0):

        self.__sampling_rate = float(sampling_rate)
        self.__approx_length = float(length)
        self.__start_frequency = float(start_frequency)
        self.__stop_frequency = float(stop_frequency)
        self.__fade_out = float(fade_out*self.__sampling_rate)
        self.__fade_in = float(fade_in*self.__sampling_rate)
        self.__excitation_factor = factor

    @sumpf.Input(float,"GetLength")
    def SetLength(self,length):
        self.__approx_length = float(length)

    def GetOutput(self):
        t = numpy.arange(0,self.GetLength()/self.__sampling_rate,1/self.__sampling_rate)
        s = numpy.sin(2*numpy.pi*self.__start_frequency*self.GetSweepParameter()*(numpy.exp(t/self.GetSweepParameter())-1))
        if self.__fade_in > 0:
            s[0:self.__fade_in] = s[0:self.__fade_in] * ((-numpy.cos(numpy.arange(self.__fade_in)/self.__fade_in*math.pi)+1) / 2)
        if self.__fade_out > 0:
            s[-self.__fade_out:] = s[-self.__fade_out:] *  ((numpy.cos(numpy.arange(self.__fade_out)/self.__fade_out*numpy.pi)+1) / 2)
        signal = sumpf.Signal(channels=(s,),samplingrate=self.__sampling_rate,labels=("Sweep signal",))
        if len(signal) % 2 != 0:
            signal = sumpf.modules.CutSignal(signal,start=0,stop=-1).GetOutput()
        signal = self.GetOutput() * signal
        return signal

    def GetReversedOutput(self, length=None):
        if length is None:
            length = self.GetLength()
        sampling_rate = self.GetOutput().GetSamplingRate()
        sweep_parameter = self.GetSweepParameter()
        # fft_len = int(2**numpy.ceil(numpy.log2(length)))
        fft_len = int(length)
        interval = numpy.linspace(0, sampling_rate/2, num=fft_len/2+1)
        inverse_sweep = 2*numpy.sqrt(interval/sweep_parameter)*numpy.exp(1j*(2*numpy.pi*sweep_parameter*interval*(self.GetStartFrequency()/interval +
                                                                     numpy.log(interval/self.GetStartFrequency()) - 1) + numpy.pi/4))
        inverse_sweep[0] = 0j
        rev_sweep = numpy.fft.irfft(inverse_sweep)
        rev_sweep = sumpf.Signal(channels=(rev_sweep,),samplingrate=sampling_rate,labels=("Reversed Sweep signal",))
        rev_sweep = (1.0/self.GetFactor())*rev_sweep
        return rev_sweep

    def GetSweepParameter(self):
        L = 1/self.__start_frequency * round((self.__approx_length/self.__sampling_rate)*
                                             self.__start_frequency/numpy.log(self.__stop_frequency/self.__start_frequency))
        return L

    @sumpf.Output(float)
    def GetLength(self):
        T_hat = self.GetSweepParameter()*numpy.log(self.__stop_frequency/self.__start_frequency)
        length = round(self.__sampling_rate*T_hat-1)
        return length

    @sumpf.Output(float)
    def GetFactor(self):
        return self.__excitation_factor

    @sumpf.Input(float,"GetFactor")
    def SetFactor(self,factor=1.0):
        self.__excitation_factor = factor

    @sumpf.Output(float)
    def GetStartFrequency(self):
        return self.__start_frequency

    @sumpf.Output(float)
    def GetStopFrequency(self):
        return self.__stop_frequency

class Cosinesweepgenerator_Novak(object):
    def __init__(self, sampling_rate=48000.0, length=2**16, start_frequency=20.0,
                 stop_frequency=20000.0, fade_out=0.02, fade_in=0.02, factor=1.0):

        self.__sampling_rate = float(sampling_rate)
        self.__approx_length = float(length)
        self.__start_frequency = float(start_frequency)
        self.__stop_frequency = float(stop_frequency)
        self.__fade_out = float(fade_out*self.__sampling_rate)
        self.__fade_in = float(fade_in*self.__sampling_rate)
        self.__excitation_factor = factor

    @sumpf.Input(float,"GetLength")
    def SetLength(self,length):
        self.__approx_length = float(length)

    @sumpf.Output(float)
    def GetFactor(self):
        return self.__excitation_factor

    @sumpf.Input(float,"GetFactor")
    def SetFactor(self,factor=1.0):
        self.__excitation_factor = factor

    def GetOutput(self):
        t = numpy.arange(0,self.GetLength()/self.__sampling_rate,1/self.__sampling_rate)
        s = numpy.cos(2*numpy.pi*self.__start_frequency*self.GetSweepParameter()*(numpy.exp(t/self.GetSweepParameter())-1))
        if self.__fade_in > 0:
            s[0:self.__fade_in] = s[0:self.__fade_in] * ((-numpy.cos(numpy.arange(self.__fade_in)/self.__fade_in*math.pi)+1) / 2)
        if self.__fade_out > 0:
            s[-self.__fade_out:] = s[-self.__fade_out:] *  ((numpy.cos(numpy.arange(self.__fade_out)/self.__fade_out*numpy.pi)+1) / 2)
        signal = sumpf.Signal(channels=(s,),samplingrate=self.__sampling_rate,labels=("Sweep signal",))
        if len(signal) % 2 != 0:
            signal = sumpf.modules.CutSignal(signal,start=0,stop=-1).GetOutput()
        signal = self.GetFactor() * signal
        return signal

    def GetReversedOutput(self, length=None):
        if length is None:
            length = self.GetLength()
        sampling_rate = self.GetOutput().GetSamplingRate()
        sweep_parameter = self.GetSweepParameter()
        # fft_len = int(2**numpy.ceil(numpy.log2(length)))
        fft_len = int(length)
        interval = numpy.linspace(0, sampling_rate/2, num=fft_len/2+1)
        inverse_sweep = 2*numpy.sqrt(interval/sweep_parameter)*numpy.exp(1j*(2*numpy.pi*sweep_parameter*interval*(self.GetStartFrequency()/interval +
                                                                                                                  numpy.log(interval/self.GetStartFrequency()) - 1) - numpy.pi/4))
        inverse_sweep[0] = 0j
        rev_sweep = numpy.fft.irfft(inverse_sweep)
        rev_sweep = sumpf.Signal(channels=(rev_sweep,),samplingrate=sampling_rate,labels=("Reversed Sweep signal",))
        rev_sweep = (1/self.GetFactor()) * rev_sweep
        return rev_sweep

    def GetSweepParameter(self):
        L = 1/self.__start_frequency * round((self.__approx_length/self.__sampling_rate)*
                                             self.__start_frequency/numpy.log(self.__stop_frequency/self.__start_frequency))
        return L

    @sumpf.Output(float)
    def GetLength(self):
        T_hat = self.GetSweepParameter()*numpy.log(self.__stop_frequency/self.__start_frequency)
        length = round(self.__sampling_rate*T_hat-1)
        return length

    @sumpf.Output(float)
    def GetStartFrequency(self):
        return self.__start_frequency

    @sumpf.Output(float)
    def GetStopFrequency(self):
        return self.__stop_frequency