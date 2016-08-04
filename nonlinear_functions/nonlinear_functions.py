import sumpf
import numpy

class NonlinearBlock(object):
    """
    An abstract base class to create a nonlinear block using nonlinear functions
    """
    @sumpf.Input(data_type=sumpf.Signal,observers=["GetOutput"])
    def SetInput(self, input_signal=None):
        """
        Set the input signal to the nonlinear block
        @param input_signal: the input signal
        """
        self._passinput.SetSignal(signal=input_signal)

    def GetOutput(self):
        """
        This method should be overridden in the derived classes. Get the output signal of the nonlinear block.
        @return: the output signal.
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

class PolynomialNonlinearBlock(NonlinearBlock):
    """
    A base class to create nonlinear block using polynomials.
    """
    def __init__(self, signal=None, degree=None):
        """
        @param signal: the input signal
        @param degree: the degree of the polynomial used in nonlinear block
        """
        if signal is None:
            self._input_signal = sumpf.Signal()
        else:
            self._input_signal = signal
        if degree is None:
            self._degree = 1
        else:
            self._degree = degree
        self._passinput = sumpf.modules.PassThroughSignal(signal=signal)

    @sumpf.Input(data_type=int,observers=["GetMaximumHarmonics"])
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
        nl_function = powerseries_expansion(degree=self._degree)
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
    def GetOutput(self):
        """
        Get the output of the nonlinear block using chebyshev polynomials.
        @return: the output signal
        """
        pass

class Hermite(PolynomialNonlinearBlock):
    """
    A class to create a nonlinear block using Hermite polynomials.
    """
    def GetOutput(self):
        """
        Get the output of the nonlinear block using Hermite polynomials.
        @return: the output signal
        """
        pass

class Legendre(PolynomialNonlinearBlock):
    """
    A class to create a nonlinear block using Legendre polynomials.
    """
    def GetOutput(self):
        """
        Get the output of the nonlinear block using Legendre polynomials.
        @return: the output signal
        """
        pass

class Clipping(NonlinearBlock):
    """
    A class to create a nonlinear block using hard clipping function.
    """
    def __init__(self, signal=None, thresholds=None):
        """
        @param signal: the input signal
        @param thresholds: the thresholds of the hard clipping function
        """
        pass

    def SetThreshold(self, thresholds=None):
        """
        Set the thresholds of the clipping function.
        @param thresholds: the thresholds Eg. [-0.8,0.8]
        """
        pass

    def GetOutput(self):
        """
        Get the output of the nonlinear block using hard clipping function.
        @return: the output signal
        """
        pass

def powerseries_expansion(degree=None):
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
    pass

def hermite_polynomial(degree=None):
    """
    A function to generate chebyshev polynomial of an array of samples.
    @param degree: the degree
    @return: the chebyshev function
    """
    pass

def legendre_polynomial(degree=None):
    """
    A function to generate chebyshev polynomial of an array of samples.
    @param degree: the degree
    @return: the chebyshev function
    """
    pass

def get_polynl_array(nl_block=None, degree_array=None):
    """
    A function to create an array of polynomial nonlinear functions.
    @param degree: the degree
    @return: the chebyshev function
    """
    pass