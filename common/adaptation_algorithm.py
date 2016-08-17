import numpy
import sumpf

class FIRAdaptationAlgorithm(object):
    """
    A base class of the FIR Adaptation algorithms.
    """
    def __init__(self, input_signal=None, desired_output=None, filter_length=None, initialcoefficients=None, step_size=None,
                 leakage=None, iteration_cycle=None):
        """
        @param input_signal: the input signal
        @param desired_output: the desired output signal
        @param filter_length: length of the filter
        @param initialcoefficients: the initial coefficients
        @param step_size: the step size
        @param leakage: the leakage value, Eg= 0-no leakage, <1-leaky filter design, >2-error
        @param iteration_cycle: the iteration cycles, multiple iteration cycles results in over adaptation
        @return:
        """
        if input_signal is None:
            self._input_signal = sumpf.Signal()
        else:
            self._input_signal = input_signal
        if desired_output is None:
            self._desired_output = sumpf.Signal()
        else:
            self._desired_output = desired_output
        if filter_length is None:
            self._filter_length = 2**10
        else:
            self._filter_length = filter_length
        self._initial_coeff = initialcoefficients
        if leakage is None:
            self._leakage = 0
        else:
            self._leakage = leakage
        if iteration_cycle is None:
            self._iteration_cycle = 1
        else:
            self._iteration_cycle = iteration_cycle
        if step_size is None:
            self._step_size = 0.1
        else:
            self._step_size = step_size

    @sumpf.Input(sumpf.Signal, "GetFilterKernel")
    def SetInput(self, input_signal):
        """
        Set the input signal for the adaptation algorithm
        @param inputsignal: the input signal
        """
        self._input_signal = input_signal

    @sumpf.Input(sumpf.Signal, "GetFilterKernel")
    def SetDesiredOutput(self, desired_output):
        """
        Set the desired output of the adaptation algorithm
        @param desired_output: the desired output signal
        """
        self._desired_output = desired_output

    @sumpf.Input(int, "GetFilterKernel")
    def SetFilterLength(self, filter_length):
        """
        Set the filter length of the adaptation algorithm
        @param filter_length: the filter length
        """
        self._filter_length = filter_length

    @sumpf.Output(sumpf.Signal)
    def GetFilterKernel(self):
        """
        Get the identified filter kernel by the adaptation algorithm. This should be overriden by the base classes.
        @return: the identified filter kernel
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

class MISO_NLMS_algorithm(FIRAdaptationAlgorithm):
    """
    A class where the MISO NLMS algorithm is implemented. If the input signals have multiple channels then filter kernels
    for multiple filters are found, else filter kernel of single filter is found.
    """
    def __init__(self, input_signal=None, desired_output=None, filter_length=None, step_size=None,
                 initialcoefficients=None, leakage=None, iteration_cycle=None, epsilon=0.0001):
        """
        @param input_signal: the input signal
        @param desired_output: the desired output signal
        @param filter_length: length of the filter
        @param step_size: the step size
        @param initialcoefficients: the initial coefficients
        @param leakage: the leakage value, Eg= 0-no leakage, <1-leaky filter design, >2-error
        @param iteration_cycle: the iteration cycles, multiple iteration cycles results in over adaptation
        @param epsilon: the regularization factor to avoid numerical errors when power of input is close to zero
        """
        self.__epsilon = epsilon
        FIRAdaptationAlgorithm.__init__(self, input_signal=input_signal, desired_output=desired_output, step_size=step_size,
                                        filter_length=filter_length, initialcoefficients=initialcoefficients,
                                        leakage=leakage, iteration_cycle=iteration_cycle)

    @sumpf.Output(sumpf.Signal)
    def GetFilterKernel(self):
        """
        Get the identified filter kernel by the adaptation algorithm. This should be overriden by the base classes.
        @return: the identified filter kernel
        """
        input_signals_array = self._input_signal.GetChannels()
        initCoeffs = self._initial_coeff
        d = self._desired_output.GetChannels()[0]
        M = self._filter_length
        channels = len(input_signals_array)
        step_size = self._step_size
        leak = self._leakage
        eps = self.__epsilon
        W = []
        N = len(input_signals_array[0]) - M + 1
        if initCoeffs is None:
            init = numpy.zeros((channels, M))
        else:
            init = initCoeffs.GetChannels()
        leakstep = (1 - step_size * leak)
        u = []  # input signal array
        w = []  # filter coefficients array
        for channel in range(channels):
            u.append(input_signals_array[channel])
            w.append(init[channel])
        E = numpy.zeros(N)
        for n in xrange(N):
            normfac = [0, ] * channels
            x = numpy.zeros((channels, M))
            y = numpy.zeros((channels, M))
            for channel in range(channels):
                x[channel] = numpy.flipud(u[channel][n:n + M])
                normfac[channel] = 1. / (numpy.dot(x[channel], x[channel]) + eps)
                y[channel] = numpy.dot(x[channel], w[channel])

            Y = numpy.sum(y, axis=0)
            e = d[n + M - 1] - Y
            E[n] = numpy.sum(e)
            for channel in range(channels):
                w[channel] = leakstep * w[channel] + step_size * normfac[channel] * x[channel] * e
        for channel in range(channels):
            W = sumpf.Signal(channels=w, samplingrate=self._input_signal.GetSamplingRate(), labels=("Identified filters",))
        return W

class SISO_NLMS_algorithm(FIRAdaptationAlgorithm):
    """
    A class where the SISO NLMS algorithm is implemented. If the input signals have multiple channels then filter kernels
    for multiple filters are found, else filter kernel of single filter is found.
    """
    def __init__(self, input_signal=None, desired_output=None, filter_length=None, step_size=None,
                 initialcoefficients=None, leakage=None, iteration_cycle=None, epsilon=0.0001):
        """
        @param input_signal: the input signal
        @param desired_output: the desired output signal
        @param filter_length: length of the filter
        @param step_size: the step size
        @param initialcoefficients: the initial coefficients
        @param leakage: the leakage value, Eg= 0-no leakage, <1-leaky filter design, >2-error
        @param iteration_cycle: the iteration cycles, multiple iteration cycles results in over adaptation
        @param epsilon: the regularization factor to avoid numerical errors when power of input is close to zero
        """
        self.__epsilon = epsilon
        FIRAdaptationAlgorithm.__init__(self, input_signal=input_signal, desired_output=desired_output, step_size=step_size,
                                        filter_length=filter_length, initialcoefficients=initialcoefficients,
                                        leakage=leakage, iteration_cycle=iteration_cycle)

    @sumpf.Output(sumpf.Signal)
    def GetFilterKernel(self):
        """
        Get the identified filter kernel by the adaptation algorithm. This should be overriden by the base classes.
        @return: the identified filter kernel
        """
        d = self._desired_output.GetChannels()[0]
        M = self._filter_length
        input_signals_array = self._input_signal.GetChannels()
        channels = len(input_signals_array)
        initCoeffs = self._initial_coeff
        step_size = self._step_size
        leak = self._leakage
        eps = self.__epsilon
        W = []
        if initCoeffs is None:
            init = numpy.zeros((channels, M))
        else:
            init = initCoeffs.GetChannels()
        leakstep = (1 - step_size * leak)

        for channel in range(channels):
            u = input_signals_array[channel]
            N = len(u) - M + 1
            w = init[channel]  # Initial coefficients
            y = numpy.zeros((channels, N))  # Filter output
            e = numpy.zeros((channels, N))  # Error signal
            for n in xrange(N):
                x = numpy.flipud(u[n:n + M])  # Slice to get view of M latest datapoints
                y[channel][n] = numpy.dot(x, w)
                e[channel][n] = d[n + M - 1] - y[channel][n]

                normFactor = 1. / (numpy.dot(x, x) + eps)
                w = leakstep * w + step_size * normFactor * x * e[channel][n]
            d = d - numpy.dot(x, w)
            W.append(w)
        return sumpf.Signal(channels=W, samplingrate=self._input_signal.GetSamplingRate(), labels=("Identified filters",))
