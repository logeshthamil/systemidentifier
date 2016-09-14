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

    :param input_signal: the input signal
    :param length: the desired length
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
        :param input_signal1: the first input signal
        :param input_signal2: the second input signal
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
        elif len(self.__input_signal1) == len(self.__input_signal2):
            self.__output_signal1 = self.__input_signal1
            self.__output_signal2 = self.__input_signal2

    @sumpf.Output(sumpf.Signal)
    def GetFirstOutput(self):
        """
        Get the first output signal.

        :return: the first output
        :rtype: sumpf.Signal
        """
        return self.__output_signal1

    @sumpf.Output(sumpf.Signal)
    def GetSecondOutput(self):
        """
        Get the second output signal.

        :return: the second output
        :rtype: sumpf.Signal
        """
        return self.__output_signal2

    @sumpf.Input(sumpf.Signal, ["GetFirstOutput", "GetSecondOutput"])
    def SetFirstInput(self, input_signal1):
        """
        Set the first input signal.

        :param input_signal1: the first input signal
        :type input_signal1: sumpf.Signal
        """
        self.__input_signal1 = input_signal1
        self._changelength()

    @sumpf.Input(sumpf.Signal, ["GetFirstOutput", "GetSecondOutput"])
    def SetSecondInput(self, input_signal2):
        """
        Set the second input signal.

        :param input_signal2: the second input signal
        :type input_signal2: sumpf.Signal
        """
        self.__input_signal2 = input_signal2
        self._changelength()


def change_length_signal(signal, length=None):
    """
    A function to change the length of signal. If the length of the signal is greater than the length then signal length
    is truncated, Else zeros are added to the signal.

    :param signal: the signal
    :param length: the length
    :return: the signal with modified length
    """
    if length is None:
        length = len(signal)
    if len(signal) >= length:
        signal = sumpf.modules.CutSignal(signal=signal, start=0, stop=length).GetOutput()
    else:
        signal = append_zeros(signal, length)
    return signal


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    """Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
         Data by Simplified Least Squares Procedures. Analytical
         Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
         W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
         Cambridge University Press ISBN-13: 9780521880688
    """
    import numpy as np
    from math import factorial

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate ** deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')


def smooth_filter_kernels(kernels=None):
    """
    Smooth the spectrum of the filter kernels, to make it suitable for curve fitting algorithm.

    :param kernels: the input filter kernels
    :type kernels: tuple
    :return: the smoothened output filter kernels
    :rtype: tuple
    """
    kernels_smooth = []
    for kernel in kernels:
        kernel_spec = sumpf.modules.FourierTransform(kernel).GetSpectrum()
        kernel_spec_channel = kernel_spec.GetChannels()[0]
        kernel_spec_channel_smooth = savitzky_golay(kernel_spec_channel, 93, 3)
        kernel_spec_smooth = sumpf.Spectrum(channels=[kernel_spec_channel_smooth, ],
                                            resolution=kernel_spec.GetResolution(),
                                            labels=kernel_spec.GetLabels())
        kernel_smooth = sumpf.modules.InverseFourierTransform(kernel_spec_smooth).GetSignal()
        kernels_smooth.append(kernel_smooth)
    return kernels_smooth


def exponentially_weighted_sum(input):
    """
    Compute the exponentially weighted sum of a signal or spectrum. The input is weighted in frequency domain.

    :param input: the input signal or spectrum
    :type input: sumpf.Signal or sumpf.Spectrum
    :return: the exponentially weighted sum
    :rtype: tuple
    """
    if isinstance(input, (sumpf.Signal)):
        ip = sumpf.modules.FourierTransform(signal=input).GetSpectrum()
    else:
        ip = input
    dummy = 0.0001
    while True:
        dummy = dummy + 0.0001
        low = 1 * (dummy ** 1)
        high = 1 * (dummy ** (len(input) - 1))
        if low > 1 and high > 10000:
            break
    energy_allchannels = []
    for c in ip.GetChannels():
        energy_singlechannel = []
        c = reversed(c)
        for i, s in enumerate(c):
            energy_singlechannel.append((abs(s)) * (1 * (dummy ** i)))
        energy_allchannels.append(numpy.sum(energy_singlechannel))
    return energy_allchannels
