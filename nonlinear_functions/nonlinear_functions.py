import sumpf
import nlsp
import numpy
import mpmath


class NonlinearBlock(object):
    """
    An abstract base class to create a nonlinear block using nonlinear functions
    """

    def __init__(self, input_signal):
        if input_signal is None:
            self._input_signal = sumpf.Signal()
        else:
            self._input_signal = input_signal

    @sumpf.Input(data_type=sumpf.Signal, observers=["GetOutput"])
    def SetInput(self, input_signal=None):
        """
        Set the input signal to the nonlinear block
        @param input_signal: the input signal
        """
        self._input_signal = input_signal

    def GetOutput(self):
        """
        This method should be overridden in the derived classes. Get the output signal of the nonlinear block.
        @return: the output signal.
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def CreateModified(self, *args, **kwargs):
        """
        This method should be overridden in the derived classes. Get a new instance of the class with or without modified
        parameters.
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

class ClippingNonlinearBlock(NonlinearBlock):
    """
    A base class to create nonlinear block by clipping signals.
    """

    def __init__(self, input_signal=None, clipping_threshold=None):
        """
        @param input_signal: the input signal
        @param clipping_threshold: the clipping threshold
        """
        NonlinearBlock.__init__(self, input_signal=input_signal)
        if clipping_threshold is None:
            self._clipping_threshold = [-1.0,1.0]
        else:
            self._clipping_threshold = clipping_threshold

    @sumpf.Input(data_type=tuple, observers=["GetMaximumHarmonics"])
    def SetClippingThreshold(self, clipping_threshold=None):
        """
        Set the clipping threshold of the clipping nonlinear block.
        @param degree: the degree (should be integer value)
        """
        self._clipping_threshold = clipping_threshold

    @sumpf.Output(data_type=int)
    def GetMaximumHarmonics(self):
        """
        Get the maximum harmonics introduced by the clipping nonlinear block.
        @return: the maximum harmonics
        """
        harmonics = 1
        return harmonics

    def CreateModified(self, input_signal=None, clipping_threshold=None):
        """
        Create a new instance of the class with or without modified parameters.
        @param signal: the input signal
        @param clipping_threshold: the clipping threshold
        @return:
        """
        if input_signal is None:
            input_signal = self._input_signal
        if clipping_threshold is None:
            clipping_threshold = self._clipping_threshold
        return self.__class__(input_signal=input_signal, clipping_threshold=clipping_threshold)

class HardClip(ClippingNonlinearBlock):
    """
    A class to create a nonlinear block using hard clipper.
    """
    @sumpf.Output(data_type=sumpf.Signal)
    def GetOutput(self):
        """
        Get the output of the nonlinear block using hard clipper.
        @return: the output signal
        """
        nl_function = hard_clip(thresholds=self._clipping_threshold)
        new_channels = []
        for c in self._input_signal.GetChannels():
            self.__dummy = c
            new_channels.append(tuple(nl_function((c))))
        return sumpf.Signal(channels=new_channels, samplingrate=self._input_signal.GetSamplingRate(),
                            labels=self._input_signal.GetLabels())

class SoftClip(ClippingNonlinearBlock):
    """
    A class to create a nonlinear block using soft clipper.
    """
    @sumpf.Output(data_type=sumpf.Signal)
    def GetOutput(self):
        """
        Get the output of the nonlinear block using soft clipper.
        @return: the output signal
        """
        nl_function = soft_clip(thresholds=self._clipping_threshold)
        new_channels = []
        for c in self._input_signal.GetChannels():
            self.__dummy = c
            new_channels.append(tuple(nl_function((c))))
        return sumpf.Signal(channels=new_channels, samplingrate=self._input_signal.GetSamplingRate(),
                            labels=self._input_signal.GetLabels())

class PolynomialNonlinearBlock(NonlinearBlock):
    """
    A base class to create nonlinear block using polynomials.
    """

    def __init__(self, input_signal=None, degree=None):
        """
        @param input_signal: the input signal
        @param degree: the degree of the polynomial used in nonlinear block
        """
        NonlinearBlock.__init__(self, input_signal=input_signal)
        if degree is None:
            self._degree = 1
        else:
            self._degree = degree

    @sumpf.Input(data_type=int, observers=["GetMaximumHarmonics"])
    def SetDegree(self, degree=None):
        """
        Set the degree of the polynomial nonlinear block.
        @param degree: the degree (should be integer value)
        """
        self._degree = degree

    @sumpf.Output(data_type=int)
    def GetMaximumHarmonics(self):
        """
        Get the maximum harmonics introduced by the polynomial nonlinear block.
        @return: the maximum harmonics
        """
        return self._degree

    def CreateModified(self, input_signal=None, degree=None):
        """
        Create a new instance of the class with or without modified parameters.
        @param signal: the input signal
        @param degree: the nonlinear degree
        @return:
        """
        if input_signal is None:
            input_signal = self._input_signal
        if degree is None:
            degree = self._degree
        return self.__class__(input_signal=input_signal, degree=degree)


class Power(PolynomialNonlinearBlock):
    """
    A class to create a nonlinear block using powers.
    """

    @sumpf.Output(data_type=sumpf.Signal)
    def GetOutput(self):
        """
        Get the output of the nonlinear block using powers.
        @return: the output signal
        """
        nl_function = power(degree=self._degree)
        new_channels = []
        for c in self._input_signal.GetChannels():
            self.__dummy = c
            new_channels.append(tuple(nl_function((c))))
        return sumpf.Signal(channels=new_channels, samplingrate=self._input_signal.GetSamplingRate(),
                            labels=self._input_signal.GetLabels())


class Chebyshev(PolynomialNonlinearBlock):
    """
    A class to create a nonlinear block using Chebyshev polynomials.
    """

    @sumpf.Output(data_type=sumpf.Signal)
    def GetOutput(self):
        """
        Get the output of the nonlinear block using chebyshev polynomials.
        @return: the output signal
        """
        nl_function = chebyshev_polynomial(degree=self._degree)
        new_channels = []
        for c in self._input_signal.GetChannels():
            self.__dummy = c
            new_channels.append(tuple(nl_function((c))))
        return sumpf.Signal(channels=new_channels, samplingrate=self._input_signal.GetSamplingRate(),
                            labels=self._input_signal.GetLabels())


class Hermite(PolynomialNonlinearBlock):
    """
    A class to create a nonlinear block using Hermite polynomials.
    """

    @sumpf.Output(data_type=sumpf.Signal)
    def GetOutput(self):
        """
        Get the output of the nonlinear block using Hermite polynomials.
        @return: the output signal
        """
        nl_function = hermite_polynomial(degree=self._degree)
        new_channels = []
        for c in self._input_signal.GetChannels():
            self.__dummy = c
            new_channels.append(tuple(nl_function((c))))
        return sumpf.Signal(channels=new_channels, samplingrate=self._input_signal.GetSamplingRate(),
                            labels=self._input_signal.GetLabels())


class Legendre(PolynomialNonlinearBlock):
    """
    A class to create a nonlinear block using Legendre polynomials.
    """

    @sumpf.Output(data_type=sumpf.Signal)
    def GetOutput(self):
        """
        Get the output of the nonlinear block using Legendre polynomials.
        @return: the output signal
        """
        nl_function = legendre_polynomial(degree=self._degree)
        new_channels = []
        for c in self._input_signal.GetChannels():
            self.__dummy = c
            new_channels.append(tuple(nl_function((c))))
        return sumpf.Signal(channels=new_channels, samplingrate=self._input_signal.GetSamplingRate(),
                            labels=self._input_signal.GetLabels())

def power(degree=None):
    """
    A function to generate power of an array of samples.
    @param degree: the degree
    @return: the power function
    """
    def func(channel):
        result = channel
        for i in range(1, degree):
            result = numpy.multiply(result, channel)
        return result
    return func


def chebyshev_polynomial(degree=None):
    """
    A function to generate chebyshev polynomial of an array of samples.
    @param degree: the degree
    @return: the chebyshev function
    """
    def func(channel):
        channell = []
        for i in range(0, len(channel)):
            channell.append(float(mpmath.chebyt(degree, channel[i])))
        return numpy.asarray(channell)
    return func


def hermite_polynomial(degree=None):
    """
    A function to generate chebyshev polynomial of an array of samples.
    @param degree: the degree
    @return: the chebyshev function
    """
    def func(channel):
        channell = []
        for i in range(0, len(channel)):
            channell.append(float(mpmath.hermite(degree, channel[i])))
        return numpy.asarray(channell)
    return func


def legendre_polynomial(degree=None):
    """
    A function to generate chebyshev polynomial of an array of samples.
    @param degree: the degree
    @return: the chebyshev function
    """
    def func(channel):
        channell = []
        for i in range(0, len(channel)):
            channell.append(float(mpmath.legendre(degree, channel[i])))
        return numpy.asarray(channell)
    return func


def hard_clip(thresholds=None):
    """
    A function which hard clips an array of samples
    @param thresholds: the thresholds of clipping
    @return: the clipping function
    """
    def func(channel):
        signal = sumpf.Signal(channels=(channel,), samplingrate=48000, labels=("nl",))
        clipped = sumpf.modules.ClipSignal(signal=signal, thresholds=thresholds)
        return numpy.asarray(clipped.GetOutput().GetChannels()[0])
    return func

def soft_clip(thresholds=None):
    """
    A function which soft clips an array of samples
    @param thresholds: the thresholds of clipping
    @return: the clipping function
    """
    def func(channel):
        signal = sumpf.Signal(channels=(channel,), samplingrate=48000, labels=("nl",))
        clipped = nlsp.sumpf.SoftClipSignal(signal=signal, thresholds=thresholds)
        return numpy.asarray(clipped.GetOutput().GetChannels()[0])
    return func
