
class NonlinearBlock(object):
    """
    An abstract base class to create a nonlinear block using nonlinear functions
    """
    def SetInput(self, input_signal=None):
        """
        Set the input signal to the nonlinear block
        @param input_signal: the input signal
        """
        pass

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
        pass

    def SetDegree(self, degree=None):
        """
        Set the degree of the polynomial nonlinear block.
        @param degree: the degree (should be integer value)
        """
        pass

    def GetMaximumHarmonics(self):
        """
        Get the maximum harmonics introduced by the polynomial nonlinear block.
        @return: the maximum harmonics
        """
        pass

class PowerseriesNonlinearBlock(PolynomialNonlinearBlock):
    """
    A class to create a nonlinear block using powers.
    """
    def GetOutput(self):
        """
        Get the output of the nonlinear block using powers.
        @return: the output signal
        """
        pass

class ChebyshevNonlinearBlock(PolynomialNonlinearBlock):
    """
    A class to create a nonlinear block using Chebyshev polynomials.
    """
    def GetOutput(self):
        """
        Get the output of the nonlinear block using chebyshev polynomials.
        @return: the output signal
        """
        pass

class HermiteNonlinearBlock(PolynomialNonlinearBlock):
    """
    A class to create a nonlinear block using Hermite polynomials.
    """
    def GetOutput(self):
        """
        Get the output of the nonlinear block using Hermite polynomials.
        @return: the output signal
        """
        pass

class LegendreNonlinearBlock(PolynomialNonlinearBlock):
    """
    A class to create a nonlinear block using Legendre polynomials.
    """
    def GetOutput(self):
        """
        Get the output of the nonlinear block using Legendre polynomials.
        @return: the output signal
        """
        pass

class ClippingNonlinearBlock(NonlinearBlock):
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

# def powerseries_expansion(degree=None):
#     """
#     A function to generate power of an array of samples.
#     @param degree: the degree
#     @return: the power function
#     """
#     pass
#
# def chebyshev_polynomial(degree=None):
#     """
#     A function to generate chebyshev polynomial of an array of samples.
#     @param degree: the degree
#     @return: the chebyshev function
#     """
#     pass
#
# def hermite_polynomial(degree=None):
#     """
#     A function to generate chebyshev polynomial of an array of samples.
#     @param degree: the degree
#     @return: the chebyshev function
#     """
#     pass
#
# def legendre_polynomial(degree=None):
#     """
#     A function to generate chebyshev polynomial of an array of samples.
#     @param degree: the degree
#     @return: the chebyshev function
#     """
#     pass
#
def get_polynomialnonlinearfunction_array(polynomialnonlinearblock=None, degree_array=None):
    """
    A function to create an array of polynomial nonlinear functions.
    @param degree: the degree
    @return: the chebyshev function
    """
    pass