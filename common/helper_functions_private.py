import numpy
import math
import sumpf


def cut_spectrum(input_spectrum, desired_frequency_range):
    """
    Cut the input spectrum to the desired frequency range. It appends zero outside the desired frequency range.
    :param input_spectrum: the input spectrum to which zero has to be appended outside the desired frequency range
    :param desired_frequency_range: the desired freqency range
    :return: the modified spectrum
    """
    channels_ip = []
    for ip in input_spectrum.GetChannels():
        channel_ip = []
        channel_op = []
        for n, i in enumerate(ip):
            if n > desired_frequency_range[0] / input_spectrum.GetResolution() and n < desired_frequency_range[1] / \
                    input_spectrum.GetResolution():
                channel_ip.append(i)
            else:
                channel_ip.append(0.0)
                channel_op.append(0.0)
        channels_ip.append(tuple(channel_ip))
    input_spectrum_modified = sumpf.Spectrum(channels=tuple(channels_ip), resolution=input_spectrum.GetResolution(),
                                             labels=input_spectrum.GetLabels())
    return input_spectrum_modified


def calculateenergy_timedomain(input_signal_or_spectrum):
    """
    Calculates the energy of the input in time domain.
    :param input: the input signal or spectrum whose energy has to be calculated
    :return: the tuple of the energy of the input signal of different channels
    """
    if isinstance(input_signal_or_spectrum, (sumpf.Spectrum)):
        ip = sumpf.modules.InverseFourierTransform(spectrum=input_signal_or_spectrum).GetSignal()
    else:
        ip = input_signal_or_spectrum
    energy_allchannels = []
    for c in ip.GetChannels():
        energy_singlechannel = []
        for s in c:
            energy_singlechannel.append(abs(s) ** 2)
        energy_allchannels.append(numpy.sum(energy_singlechannel))
    return energy_allchannels


def calculateenergy_freqdomain(input_signal_or_spectrum):
    """
    Calculates the energy of the input in frequency domain
    :param input: the input signal or spectrum whose energy has to be calculated
    :return: the tuple of the energy of the input spectrum of different channels
    """
    if isinstance(input_signal_or_spectrum, (sumpf.Signal)):
        ip = sumpf.modules.FourierTransform(signal=input_signal_or_spectrum).GetSpectrum()
    else:
        ip = input_signal_or_spectrum
    energy_allchannels = []
    for c in ip.GetChannels():
        energy_singlechannel = []
        for s in c:
            energy_singlechannel.append(abs(s) ** 2)
        energy_allchannels.append(numpy.sum(energy_singlechannel))
    return energy_allchannels


def calculateenergy_betweenfreq_freqdomain(input_signal_or_spectrum, desired_frequency_range):
    """
    Calculates the energy of input signal between certain frequencies of input signal
    :param input: the input signal or spectrum whose energy has to be calculated
    :param frequency_range: the range of frequencies over which the energy has to be calculated
    :return: the tuple of the energy of input spectrum in frequency domain
    """
    if isinstance(input_signal_or_spectrum, (sumpf.Signal)):
        ip = sumpf.modules.FourierTransform(signal=input_signal_or_spectrum).GetSpectrum()
    else:
        ip = input_signal_or_spectrum
    spec = cut_spectrum(ip, desired_frequency_range)
    energy = calculateenergy_freqdomain(spec)
    return energy


def append_zeros(input_signal, length=None):
    """
    Appends zeros until the signal has the given length. If no length is given,
    zeros will be appended until the length is a power of 2.
    @param input_signal: the input signal
    @param length: the desired length
    """
    if length is None:
        length = 2 ** int(math.ceil(math.log(len(input_signal), 2)))
    zeros = length - len(input_signal)
    result = sumpf.Signal(channels=tuple([c + (0.0,) * zeros for c in input_signal.GetChannels()]),
                          samplingrate=input_signal.GetSamplingRate(),
                          labels=input_signal.GetLabels())
    return result


class CheckEqualLength(object):
    """
    Check the length of two signals. In case of mismatch it will append zeros to make it equal.
    """

    def __init__(self, input_signal1=None, input_signal2=None):
        """
        @param input_signal1: the first input signal
        @param input_signal2: the second input signal
        """
        # Get the input parameters
        if input_signal1 is None:
            self.__input_signal1 = sumpf.Signal()
        else:
            self.__input_signal1 = input_signal1

        if input_signal2 is None:
            self.__input_signal2 = sumpf.Signal()
        else:
            self.__input_signal2 = input_signal2

        self.__output_signal1 = self.__input_signal1
        self.__output_signal2 = self.__input_signal2
        self._changelength()

    def _changelength(self):
        if len(self.__input_signal1) > len(self.__input_signal2):
            self.__output_signal2 = append_zeros(input_signal=self.__input_signal2, length=len(self.__input_signal1))
            self.__output_signal1 = self.__input_signal1
        elif len(self.__input_signal2) > len(self.__input_signal1):
            self.__output_signal1 = append_zeros(self.__input_signal1, len(self.__input_signal2))
            self.__output_signal2 = self.__input_signal2

    @sumpf.Output(sumpf.Signal)
    def GetFirstOutput(self):
        return self.__output_signal1

    @sumpf.Output(sumpf.Signal)
    def GetSecondOutput(self):
        return self.__output_signal2

    @sumpf.Input(sumpf.Signal, ["GetFirstOutput", "GetSecondOutput"])
    def SetFirstInput(self, input_signal1):
        self.__input_signal1 = input_signal1
        self._changelength()

    @sumpf.Input(sumpf.Signal, ["GetFirstOutput", "GetSecondOutput"])
    def SetSecondInput(self, input_signal2):
        self.__input_signal2 = input_signal2
        self._changelength()

def change_length_signal(signal, length=None):
    """
    A function to change the length of signal. If the length of the signal is greater than the length then signal length
    is truncated, Else zeros are added to the signal.
    @param signal: the signal
    @param length: the length
    @return: the signal with modified length
    """
    if length is None:
        length = len(signal)
    if len(signal) >= length:
        signal = sumpf.modules.CutSignal(signal=signal,start=0,stop=length).GetOutput()
    else:
        signal = append_zeros(signal,length)
    return signal