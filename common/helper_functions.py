import random
import sumpf


def create_arrayof_bpfilter(start_frequency=20.0, stop_frequency=20000.0, branches=5, sampling_rate=None,
                            filter_length=None):
    """
    Generates logarithmically seperated band pass filters between start and stop frequencies.

    :param start_frequency: the start frequency of the bandpass filter
    :param stop_frequency: the stop frequency of the bandpass filter
    :param branches: the number of branches of bandpass filter
    :param samplingrate: the sampling rate
    :return: a tuple of filter spectrums
    """
    if filter_length is None:
        filter_length = 2 ** 10
    if sampling_rate is None:
        sampling_rate = 48000
    ip_prp = sumpf.modules.ChannelDataProperties()
    ip_prp.SetSamplingRate(sampling_rate)
    ip_prp.SetSignalLength(filter_length)
    dummy = 10
    while True:
        dummy = dummy - 0.1
        low = 100 * (dummy ** 1)
        high = 100 * (dummy ** branches)
        if low > start_frequency * 2 and high < stop_frequency:
            break
    frequencies = []
    for i in range(1, branches + 1):
        frequencies.append(100 * (dummy ** i))
    filter_spec = []
    for freq in frequencies:
        spec = (sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              frequency=freq,
                                              resolution=ip_prp.GetResolution(),
                                              length=ip_prp.GetSpectrumLength()).GetSpectrum()) * \
               (sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              frequency=freq / 2, transform=True,
                                              resolution=ip_prp.GetResolution(),
                                              length=ip_prp.GetSpectrumLength()).GetSpectrum())
        filter_spec.append(sumpf.modules.InverseFourierTransform(spec).GetSignal())
    return filter_spec

def create_arrayof_simplefilter(start_frequency=20.0, stop_frequency=20000.0, branches=5, sampling_rate=None,
                            filter_length=None, filter_order=10):
    """
    Generates logarithmically seperated Chebyshev lowpass filters between start and stop frequencies.

    :param start_frequency: the start frequency of the bandpass filter
    :param stop_frequency: the stop frequency of the bandpass filter
    :param branches: the number of branches of bandpass filter
    :param samplingrate: the sampling rate
    :return: a tuple of filter spectrums
    """
    if filter_length is None:
        filter_length = 2 ** 10
    if sampling_rate is None:
        sampling_rate = 48000
    ip_prp = sumpf.modules.ChannelDataProperties()
    ip_prp.SetSamplingRate(sampling_rate)
    ip_prp.SetSignalLength(filter_length)
    dummy = 10
    while True:
        dummy = dummy - 0.1
        low = 100 * (dummy ** 1)
        high = 100 * (dummy ** branches)
        if low > start_frequency * 2 and high < stop_frequency:
            break
    frequencies = []
    for i in range(1, branches + 1):
        frequencies.append(100 * (dummy ** i))
    filter_spec = []
    for freq in frequencies:
        spec = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.CHEBYCHEV1(order=filter_order),
                                              frequency=freq,
                                              resolution=ip_prp.GetResolution(),
                                              length=ip_prp.GetSpectrumLength()).GetSpectrum()
        filter_spec.append(sumpf.modules.InverseFourierTransform(spec).GetSignal())
    return filter_spec

def create_arrayof_complexfilters(start_frequency=20.0, stop_frequency=20000.0, branches=5, sampling_rate=None,
                                    filter_length=None, filter_order=15):
    """
    Generates logarithmically seperated complex band pass filters between start and stop frequencies.

    :param start_frequency: the start frequency of the bandpass filter
    :param stop_frequency: the stop frequency of the bandpass filter
    :param branches: the number of branches of bandpass filter
    :param samplingrate: the sampling rate
    :return: a tuple of filter spectrums
    """
    if filter_length is None:
        filter_length = 2 ** 10
    if sampling_rate is None:
        sampling_rate = 48000
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSamplingRate(sampling_rate)
    prp.SetSignalLength(filter_length)
    dummy = 10
    while True:
        dummy = dummy - 0.1
        low = 100 * (dummy ** 1)
        high = 100 * (dummy ** branches)
        if low > start_frequency * 2 and high < stop_frequency:
            break
    frequencies = []
    for i in range(1, branches + 1):
        frequencies.append(100 * (dummy ** i))
    filter_spec = []
    for freq in frequencies:
        spec = sumpf.modules.FilterGenerator(filterfunction = sumpf.modules.FilterGenerator.CHEBYCHEV1(order=filter_order, ripple=1), frequency=freq, resolution=prp.GetResolution(), length=prp.GetSpectrumLength(), transform=True).GetSpectrum() + \
               sumpf.modules.WeightingFilterGenerator(resolution=prp.GetResolution(), length=prp.GetSpectrumLength()).GetSpectrum() + \
               sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.CHEBYCHEV1(order=filter_order, ripple=1), frequency=freq, resolution=prp.GetResolution(), length=prp.GetSpectrumLength(), transform=False).GetSpectrum() + \
               sumpf.modules.WeightingFilterGenerator(resolution=prp.GetResolution(), length=prp.GetSpectrumLength(), weighting=sumpf.modules.WeightingFilterGenerator.C).GetSpectrum()
        filter_spec.append(sumpf.modules.InverseFourierTransform(spec).GetSignal())
    return filter_spec