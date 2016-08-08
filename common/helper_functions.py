import random
import sumpf
import nlsp

def create_arrayof_bpfilter(start_freq=20.0, stop_freq=20000.0, branches=5, sampling_rate=48000, amplify=False):
    """
    Generates logarithmically seperated band pass filters between start and stop frequencies.
    :param start_freq: the start frequency of the bandpass filter
    :param stop_freq: the stop frequency of the bandpass filter
    :param branches: the number of branches of bandpass filter
    :param input: the input signal to get the filter parameters
    :return: a tuple of filter spectrums, and the list of frequencies
    """
    ip_prp = sumpf.modules.ChannelDataProperties()
    ip_prp.SetSamplingRate(samplingrate=sampling_rate)
    dummy = 10
    while True:
        dummy = dummy - 0.1
        low = 100 * (dummy**1)
        high = 100 * (dummy**branches)
        if low > start_freq*2 and high < stop_freq:
            break
    frequencies = []
    for i in range(1,branches+1):
        frequencies.append(100 * (dummy**i))
    filter_spec = []
    for freq in frequencies:
        spec =  (sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                            frequency=freq,
                                            resolution=ip_prp.GetResolution(),
                                            length=ip_prp.GetSpectrumLength()).GetSpectrum())*\
                (sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                            frequency=freq/2,transform=True,
                                            resolution=ip_prp.GetResolution(),
                                            length=ip_prp.GetSpectrumLength()).GetSpectrum())
        if amplify is True:
            spec = sumpf.modules.Multiply(value1=spec,value2=random.randint(10,100)).GetResult()
        filter_spec.append(sumpf.modules.InverseFourierTransform(spec).GetSignal())
    # filter_spec = [i for i in reversed(filter_spec)]
    return filter_spec

def create_arrayof_nlfunctions(function,branches):
    nl = []
    for i in range(1,branches+1):
        nl.append(function(degree=i))
    return nl