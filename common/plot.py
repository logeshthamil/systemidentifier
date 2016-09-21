import collections
import math
import sumpf
import matplotlib.pyplot as pyplot
import numpy

max_freq = 40000.0
scale_log = False
axis = pyplot.subplot(111)


def _dBlabel(y, pos):
    if y <= 0.0:
        return "0.0"
    else:
        spl = 20.0 * math.log(y, 10)
        return "%.1f dB" % spl


def _log():
    dBformatter = pyplot.FuncFormatter(_dBlabel)
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.yaxis.set_major_formatter(dBformatter)
    #	axis.yaxis.set_minor_formatter(dBformatter)
    globals()["scale_log"] = True


def _reset_color_cycle():
    cc = axis._get_lines.color_cycle
    while cc.next() != "k":
        pass


def _show():
    """
    Show the plots.
    """
    pyplot.show()
    globals()["axis"] = pyplot.subplot(111)
    if scale_log:
        _log()



def plot_signalorspectrum(signalorspectrum, legend=True, show=True, line='-'):
    """
    A function to plot a signal or spectrum.

    :param signalorspectrum: the input signal or spectrum
    :type signalorspectrum: sumpf.Signal or sumpf.Spectrum
    :param legend: automotically set the legend handles
    :type legend: bool
    :param show: show the plot of the input signal or spectrum
    :type show: bool
    :param line: type of line
    :type line: matplotlib line parameter
    :return: plot the input signal or spectrum
    """
    data = signalorspectrum
    if not isinstance(data, collections.Iterable):
        data = [data]
    else:
        data = data
    if isinstance(data[0], sumpf.Spectrum):
        _log()
        for d in data:
            # create x_data
            x_data = []
            for i in range(len(d)):
                x_data.append(i * d.GetResolution())
            # plot
            for i in range(len(d.GetMagnitude())):
                pyplot.plot(x_data, d.GetMagnitude()[i], line, label=d.GetLabels()[i])
                #				pyplot.plot(x_data[0:len(x_data) // 2], d.GetPhase()[i][0:len(x_data) // 2], label=d.GetLabels()[i])
                #				pyplot.plot(x_data, d.GetGroupDelay()[i], label=d.GetLabels()[i])
        pyplot.xlim((0.0, max_freq))
        axis.set_xlabel("Frequeny [Hz]", fontsize="x-large")
    else:
        for d in data:
            # create x_data
            x_data = []
            for i in range(len(d)):
                x_data.append(float(i) // d.GetSamplingRate())
            # plot
            for i in range(len(d.GetChannels())):
                pyplot.plot(x_data, d.GetChannels()[i], label=d.GetLabels()[i])
        axis.set_xlabel("Time [s]", fontsize="x-large")
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if show:
        _show()


def plot_groupdelayandmagnitude(signalorspectrumarray, legend=True, show=True):
    """
    Plot the group delay and magnitude of a spectrum in the same plot.

    :param signalorspectrumarray: the array of the input signals or spectrums
    :type signalorspectrumarray: tuple
    :param legend: automatically sets the legend handles
    :type legend: bool
    :param show: shoe the plot of the input signal or spectrum
    :type show: bool
    :return: plot the group delay and magnitude of the spectrum in the same plot
    """
    data = signalorspectrumarray
    if not isinstance(data, collections.Iterable):
        data = [data]
    if isinstance(data[0], sumpf.Spectrum):
        for d in data:
            # create x_data
            x_data = []
            for i in range(len(d)):
                x_data.append(i * d.GetResolution())
            # plot
            for i in range(len(d.GetMagnitude())):
                ax = pyplot.subplot(2, 1, 1)
                pyplot.title("Frequency")
                pyplot.loglog(x_data, d.GetMagnitude()[i], label=d.GetLabels()[i])
                pyplot.subplot(2, 1, 2, sharex=ax)
                pyplot.title("Group delay")
                pyplot.semilogx(x_data, d.GetGroupDelay()[i], label=d.GetLabels()[i])
    else:
        for d in data:
            # create x_data
            d = sumpf.modules.FourierTransform(d).GetSpectrum()
            x_data = []
            for i in range(len(d)):
                x_data.append(i * d.GetResolution())
            # plot
            for i in range(len(d.GetMagnitude())):
                ax = pyplot.subplot(2, 1, 1)
                pyplot.title("Frequency")
                pyplot.loglog(x_data, d.GetMagnitude()[i], label=d.GetLabels()[i])
                pyplot.subplot(2, 1, 2, sharex=ax)
                pyplot.title("Group delay")
                pyplot.semilogx(x_data, d.GetGroupDelay()[i], label=d.GetLabels()[i])
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if show:
        _show()


def relabelandplot(input, label=None, show=True, save=False, name=None, line="-"):
    """
    Relabel the input signal or spectrum and plot

    :param input: the input signal or spectrum
    :param label: the label text
    :param show: True or False
    :return: plots the given input with label
    """
    relabelled = input
    if isinstance(relabelled, sumpf.Spectrum):
        _log()
    plot_signalorspectrum(relabelled, show=show, line=line)


def plot_array(input_array, label_array=None, save=False, name=None, Show=True):
    """
    Helper function to plot array

    :param input_array: the input array of signal or spectrum
    :param label_array: the array of labels
    :return: the plot of the input array with labels
    """
    if label_array is None:
        label_array = ["none", ] * len(input_array)
    for input, label in zip(input_array, label_array):
        relabelandplot(input, label, False, save, name)
    if Show is True:
        _show()


def plot_filterkernelsofHGM(input_array, show=True, freq=True):
    """
    A function to plot the filter kernels of the HGM.

    :param input_array: the array of filter kernels
    :type input_array: tuple of sumpf.Signal
    :param show: show the plots of the filter kernels
    :type show: bool
    :param freq: plot the filter kernels in frequency or time domain, True to plot in frequency domain
    :type freq: bool
    :return: plot the filter kernels
    """
    if freq is True:
        for input in input_array:
            input = sumpf.modules.FourierTransform(input).GetSpectrum()
            plot_signalorspectrum(input, show=False)
    else:
        for input in input_array:
            plot_signalorspectrum(input, show=False)
    if show is True:
        _show()


def plot_simplearray(x_array=None, y_array=None, x_label=None, y_label=None, label=None, show=True):
    """
    Plot a simple two dimensional array

    :param x_array: elements of x axis
    :type x_array: tuple
    :param y_array: elements of y axis
    :type y_array: tuple
    :param x_label: x label
    :type x_label: str
    :param y_label: y label
    :type y_label: str
    :param label: label for the entire plot
    :type label: str
    :param show: shot the plot
    :type show: bool
    :return: plot a simple 2d array
    """
    pyplot.plot(x_array, y_array, label=label)
    pyplot.ylabel(y_label)
    pyplot.xlabel(x_label)
    pyplot.legend(loc='upper center', shadow=True)
    if show is True:
        pyplot._show()


def plot_PDF(signalorspectrum, legend=True, show=True):
    """
    Plot the Probablity Density Function of a signal.

    :param signalorspectrum: the input signal or spectrum
    :type signalorspectrum: sumpf.Signal or sumpf.Spectrum
    :param legend: automatically sets the legend handles
    :type legend: bool
    :param show: plot the PDF of the input signal
    :type show: bool
    :return: plots the PDF of the input signal or spectrum
    """
    data = signalorspectrum
    if not isinstance(data, collections.Iterable):
        data = [data]
    else:
        data = data
    if isinstance(data[0], sumpf.Spectrum):
        for d in data:
            de = sumpf.modules.InverseFourierTransform(d).GetSignal()
            for i in range(len(de.GetChannels())):
                pyplot.hist(de.GetChannels()[i], bins=500)
    else:
        for d in data:
            for i in range(len(d.GetChannels())):
                pyplot.hist(d.GetChannels()[i], bins=500)
    axis.set_xlabel("Value", fontsize="x-large")
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if show:
        _show()


""" short time fourier transform of audio signal """
from numpy.lib import stride_tricks

def _stft(sig, frameSize, overlapFac=0.5, window=numpy.hanning):
    win = window(frameSize)
    hopSize = int(frameSize - numpy.floor(overlapFac * frameSize))

    # zeros at beginning (thus center of 1st window should be for sample nr. 0)
    samples = numpy.append(numpy.zeros(numpy.floor(frameSize / 2.0)), sig)
    # cols for windowing
    cols = numpy.ceil((len(samples) - frameSize) / float(hopSize)) + 1
    # zeros at end (thus samples can be fully covered by frames)
    samples = numpy.append(samples, numpy.zeros(frameSize))

    frames = stride_tricks.as_strided(samples, shape=(cols, frameSize),
                                      strides=(samples.strides[0] * hopSize, samples.strides[0])).copy()
    frames *= win

    return numpy.fft.rfft(frames)


""" scale frequency axis logarithmically """


def _logscale_spec(spec, sr=44100, factor=100.):
    timebins, freqbins = numpy.shape(spec)
    scale = numpy.linspace(0, 1, freqbins) ** factor
    scale *= (freqbins - 1) / max(scale)
    scale = numpy.unique(numpy.round(scale))

    # create spectrogram with new freq bins
    newspec = numpy.complex128(numpy.zeros([timebins, len(scale)]))
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            newspec[:, i] = numpy.sum(spec[:, scale[i]:], axis=1)
        else:
            newspec[:, i] = numpy.sum(spec[:, scale[i]:scale[i + 1]], axis=1)

    # list center freq of bins
    allfreqs = numpy.abs(numpy.fft.fftfreq(freqbins * 2, 1. / sr)[:freqbins + 1])
    freqs = []
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            freqs += [numpy.mean(allfreqs[scale[i]:])]
        else:
            freqs += [numpy.mean(allfreqs[scale[i]:scale[i + 1]])]

    return newspec, freqs


""" plot spectrogram"""


def plotspectrogram(audio, binsize=2 ** 12, plotpath=None, colormap="rainbow"):
    """
    Plot the spectrogram path
    :param audio: the input signal
    :type audio: sumpf.Signal
    :param binsize: the bin size
    :type binsize: int
    :param plotpath: the path for saving the spectrogram as image
    :type plotpath: str
    :param colormap: the colormap
    :type colormap: matplotlib colormap
    :return: plot the spectrogram of the sumpf.Signal
    """
    samplerate = audio.GetSamplingRate()
    samples = audio.GetChannels()[0]
    s = _stft(samples, binsize)

    sshow, freq = _logscale_spec(s, sr=samplerate)
    ims = 20. * numpy.log10(numpy.abs(sshow) / 10e-6)  # amplitude to decibel

    timebins, freqbins = numpy.shape(ims)

    pyplot.imshow(numpy.transpose(ims), origin="lower", aspect="auto", cmap=colormap, interpolation="none")
    pyplot.colorbar()

    pyplot.xlabel("time (s)")
    pyplot.ylabel("frequency (hz)")
    pyplot.xlim([0, timebins - 1])
    pyplot.ylim([0, freqbins])

    xlocs = numpy.float32(numpy.linspace(0, timebins - 1, 5))
    pyplot.xticks(xlocs, ["%.02f" % l for l in ((xlocs * len(samples) / timebins) + (0.5 * binsize)) / samplerate])
    ylocs = numpy.int16(numpy.round(numpy.linspace(0, freqbins - 1, 10)))
    pyplot.yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])

    if plotpath:
        pyplot.savefig(plotpath, bbox_inches="tight")
    else:
        pyplot.show()