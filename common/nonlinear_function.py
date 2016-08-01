import sumpf
import sympy.mpmath as mpmath
import numpy
import nlsp

class NonlinearFunction(object):
    """
    Generates the nonlinear output of the input signal. The nonlinearity is introduced by the power series expansion or
    by applying orthogonal polynomials of the input signal.
    This NonlinearFunction class imports modules from sympy.mpmath to generate the orthogonal polynomials and this uses
    numpy.multiply to generate the power series expansion
    """

    @staticmethod
    def power_series(degree, signal=None):
        return NonlinearFunction(signal=signal, nonlin_func=nlsp.function_factory.power_series(degree), max_harm=degree)

    @staticmethod
    def hermite_polynomial(degree, signal=None):
        return NonlinearFunction(signal=signal, nonlin_func=nlsp.function_factory.hermite_polynomial(degree),
                                 max_harm=degree)

    @staticmethod
    def legrendre_polynomial(degree, signal=None):
        return NonlinearFunction(signal=signal, nonlin_func=nlsp.function_factory.legrendre_polynomial(degree),
                                 max_harm=degree)

    @staticmethod
    def chebyshev1_polynomial(degree, signal=None):
        return NonlinearFunction(signal=signal, nonlin_func=nlsp.function_factory.chebyshev1_polynomial(degree),
                                 max_harm=degree)

    @staticmethod
    def chebyshev2_polynomial(degree, signal=None):
        return NonlinearFunction(signal=signal, nonlin_func=nlsp.function_factory.chebyshev2_polynomial(degree),
                                 max_harm=degree)

    @staticmethod
    def laguerre_polynomial(degree, signal=None):
        return NonlinearFunction(signal=signal, nonlin_func=nlsp.function_factory.laguerre_polynomial(degree),
                                 max_harm=degree)

    @staticmethod
    def clipping(threshold, signal=None):
        return NonlinearFunction(signal=signal, nonlin_func=nlsp.function_factory.clipsignal(threshold),
                                 max_harm=1)


    def __init__(self, signal=None, nonlin_func=lambda x: x, max_harm=1):
        """
        :param signal: the input Signal
        :param nonlin_func: a callable object, that expects a Signal's channel as an iterable, and returns a nonlinear distorted version of it
        :param max_harm: the maximum produced harmonic of the nonlinear distortion
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__nonlin_func = nonlin_func
        self.__max_harm = max_harm

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.__signal = signal

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetNonlinearFunction(self, nonlin_func):
        self.__nonlin_func = nonlin_func

    @sumpf.Input(int,"GetMaximumHarmonic")
    def SetMaximumHarmonic(self, max_harm):
        self.__max_harm = max_harm

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        new_channels = []
        for c in self.__signal.GetChannels():
            self.__dummy = c
            new_channels.append(tuple(self.__nonlin_func((c))))
        return sumpf.Signal(channels=new_channels, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

    @sumpf.Output(int)
    def GetMaximumHarmonic(self):
        return self.__max_harm
