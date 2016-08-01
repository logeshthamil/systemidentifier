import numpy
import mpmath
import sumpf

def power_series(degree):
    def func(channel):
        result = channel
        for i in range(1, degree):
            result = numpy.multiply(result, channel)
        return result
    return func

def legrendre_polynomial(degree):
    def func(channel):
        channell = []
        for i in range(0,len(channel)):
            channell.append(float(mpmath.legendre(degree,channel[i])))
        return numpy.asarray(channell)
    return func

def chebyshev1_polynomial(degree):
    def func(channel):
        channell = []
        for i in range(0,len(channel)):
            channell.append(float(mpmath.chebyt(degree,channel[i])))
        return numpy.asarray(channell)
    return func

def chebyshev2_polynomial(degree):
    def func(channel):
        channell = []
        for i in range(0,len(channel)):
            channell.append(float(mpmath.chebyu(degree,channel[i])))
        return numpy.asarray(channell)
    return func

def hermite_polynomial(degree):
    def func(channel):
        channell = []
        for i in range(0,len(channel)):
            channell.append(float(mpmath.hermite(degree,channel[i])))
        return numpy.asarray(channell)
    return func

def laguerre_polynomial(degree):
    def func(channel):
        channell = []
        for i in range(0,len(channel)):
            channell.append(float(mpmath.laguerre(degree,0,channel[i])))
        return numpy.asarray(channell)
    return func

def hardclip(threshold):
    def func(channel):
        signal = sumpf.Signal(channels=(channel,), samplingrate=48000, labels=("nl",))
        clipped = sumpf.modules.ClipSignal(signal=signal,thresholds=threshold)
        return numpy.asarray(clipped.GetOutput().GetChannels()[0])
    return func