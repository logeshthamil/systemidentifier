import random
import sumpf

def create_arrayof_bpfilter(start_freq=20.0, stop_freq=20000.0, branches=5, sampling_rate=48000, amplify=False):
    # TODO: In order to avoid confusing the user, I suggest, that you use the same parameter names as in SuMPF:
    #    start_frequency, stop_frequency and samplingrate    (as for example in the SweepGenerator)
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
        low = 100 * (dummy ** 1)
        high = 100 * (dummy ** branches)
        if low > start_freq * 2 and high < stop_freq:
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
        if amplify is True: # TODO: "if amplify:", don't compare with booleans and especially, don't do that with "is"
            spec = sumpf.modules.Multiply(value1=spec, value2=random.randint(10, 100)).GetResult()
            # TODO: the algebra classes (Multiply etc.) are mainly to create signal processing chains.
            #    If you are not creating signal processing chains, there is an easier way:
            #    spec = spec * random.randint(10, 100)
            # TODO: Don't use the convenience instance of the RNG in random (a reason for this is in the Pythonist Manifesto [1.4 Global State]).
            #    Create your own instance and allow to seed it with a parameter.
        filter_spec.append(sumpf.modules.InverseFourierTransform(spec).GetSignal())
    # filter_spec = [i for i in reversed(filter_spec)]
    return filter_spec

def create_arrayof_nlfunctions(function, branches):
    # TODO: this function is not really necessary. it can be replaced by one-liners like:
    #    nonlinear_functions = [nlsp.nonlinear_functions.Power(degree=i+1) for i in range(branches)]
    # this is clearer, because you don't have to look up, what this function does,
    # it is more versatile and it avoids terms like "branches", which are only
    # defined as you intended in the context of HGMs. And it is likely to be faster.
    nl = []
    for i in range(1, branches + 1):
        nl.append(function(degree=i))
    return nl
