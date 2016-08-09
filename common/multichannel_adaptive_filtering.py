import numpy

def siso_nlms_multichannel(input_signals_array, desired_output, filter_length, step_size, eps=0.001, leak=0, initCoeffs=None):
    """
    A function to adapt multiple filter coefficients based on multiple input and single output. It uses individual nlms
    algorithm to adapt the filter coefficients.
    @param input_signals_array: the array of multiple input signals
    @param desired_output: the desired output signal
    @param filter_length: number of taps in the filter
    @param step_size: the step size of adaptation
    @param eps: the epsilon value
    @param leak: the leak value
    @param initCoeffs: the array of filter kernels which are used for initialization
    @return: the multiple filter kernels
    """
    d = desired_output
    M = filter_length
    N = None
    channels = len(input_signals_array)
    W = []
    if initCoeffs is None:
        init = numpy.zeros((channels,M))
    else:
        init = initCoeffs
    leakstep = (1 - step_size*leak)

    for channel in range(channels):
        u = input_signals_array[channel]
        if N is None:
            N = len(u)-M+1
        w = init[channel]           # Initial coefficients
        y = numpy.zeros((channels,N))  # Filter output
        e = numpy.zeros((channels,N))  # Error signal
        for n in xrange(N):
            x = numpy.flipud(u[n:n+M])  # Slice to get view of M latest datapoints
            y[channel][n] = numpy.dot(x, w)
            e[channel][n] = d[n+M-1] - y[channel][n]

            normFactor = 1./(numpy.dot(x, x) + eps)
            w = leakstep * w + step_size * normFactor * x * e[channel][n]
        d = d - numpy.dot(x, w)
        W.append(w)
    return W

def miso_nlms_multichannel(input_signals_array, desired_output, filter_length, step_size, eps=0.001, leak=0, initCoeffs=None):
    """
    A function to adapt multiple filter coefficients based on multiple input and single output. It uses a MISO NLMS
    algorithm to adapt the filter coefficients.
    @param input_signals_array: the array of multiple input signals
    @param desired_output: the desired output signal
    @param filter_length: number of taps in the filter
    @param step_size: the step size of adaptation
    @param eps: the epsilon value
    @param leak: the leak value
    @param initCoeffs: the array of filter kernels which are used for initialization
    @return: the multiple filter kernels
    """
    d = desired_output
    M = filter_length
    N = None
    channels = len(input_signals_array)
    W = []
    if N is None:
        N = len(input_signals_array[0])-M+1
    if initCoeffs is None:
        init = numpy.zeros((channels,M))
    else:
        init = initCoeffs
    leakstep = (1 - step_size*leak)
    u = []                      # input signal array
    w = []                      # filter coefficients array
    for channel in range(channels):
        u.append(input_signals_array[channel])
        w.append(init[channel])
    E = numpy.zeros(N)
    for n in xrange(N):
        normfac = [0,]*channels
        x = numpy.zeros((channels,M))
        y = numpy.zeros((channels,M))
        for channel in range(channels):
            x[channel] = numpy.flipud(u[channel][n:n+M])
            normfac[channel] = 1./(numpy.dot(x[channel], x[channel]) + eps)
            y[channel] = numpy.dot(x[channel], w[channel])

        Y = numpy.sum(y,axis=0)
        e = d[n+M-1] - Y
        E[n] = numpy.sum(e)
        for channel in range(channels):
            w[channel] = leakstep * w[channel] + step_size * normfac[channel] * x[channel] * e
    for channel in range(channels):
        W.append(w[channel])
    return W