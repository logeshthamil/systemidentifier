import numpy
import sumpf

def cut_spectrum(inputspectrum,freq_range):
    """
    Appends zero outside the desired frequency range of the spectrum.
    :param inputspectrum: the input spectrum to which zero has to be appended outside the desired frequency range
    :param freq_range: the desired freqency range
    :return: the modified spectrum
    """
    channels_ip = []
    for ip in inputspectrum.GetChannels():
        channel_ip = []
        channel_op = []
        for n,i in enumerate(ip):
            if n > freq_range[0]/inputspectrum.GetResolution() and n < freq_range[1]/inputspectrum.GetResolution():
                channel_ip.append(i)
            else:
                channel_ip.append(0.0)
                channel_op.append(0.0)
        channels_ip.append(tuple(channel_ip))
    input_spectrum = sumpf.Spectrum(channels=tuple(channels_ip), resolution=inputspectrum.GetResolution(),
                                  labels=inputspectrum.GetLabels())
    return input_spectrum

def calculateenergy_timedomain(input):
    """
    Calculates the energy of the input in time domain.
    :param input: the input signal or spectrum whose energy has to be calculated
    :return: the tuple of the energy of the input signal of different channels
    """
    if isinstance(input,(sumpf.Spectrum)):
        ip = sumpf.modules.InverseFourierTransform(spectrum=input).GetSignal()
    else:
        ip = input
    energy_allchannels = []
    for c in ip.GetChannels():
        energy_singlechannel = []
        for s in c:
            energy_singlechannel.append(abs(s)**2)
        energy_allchannels.append(numpy.sum(energy_singlechannel))
    return energy_allchannels

def calculateenergy_freqdomain(input):
    """
    Calculates the energy of the input in frequency domain
    :param input: the input signal or spectrum whose energy has to be calculated
    :return: the tuple of the energy of the input spectrum of different channels
    """
    if isinstance(input,(sumpf.Signal)):
        ip = sumpf.modules.FourierTransform(signal=input).GetSpectrum()
    else:
        ip = input
    energy_allchannels = []
    for c in ip.GetChannels():
        energy_singlechannel = []
        for s in c:
            energy_singlechannel.append(abs(s)**2)
        energy_allchannels.append(numpy.sum(energy_singlechannel))
    return energy_allchannels

def calculateenergy_betweenfreq_freqdomain(input,frequency_range):
    """
    Calculates the energy of input signal between certain frequencies of input signal
    :param input: the input signal or spectrum whose energy has to be calculated
    :param frequency_range: the range of frequencies over which the energy has to be calculated
    :return: the tuple of the energy of input spectrum in frequency domain
    """
    if isinstance(input,(sumpf.Signal)):
        ip = sumpf.modules.FourierTransform(signal=input).GetSpectrum()
    else:
        ip = input
    spec = cut_spectrum(ip,frequency_range)
    energy = calculateenergy_freqdomain(spec)
    return energy