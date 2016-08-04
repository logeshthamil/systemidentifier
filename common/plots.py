import numpy
import collections
import math
import sumpf
import nlsp
from scipy import signal
import matplotlib.pyplot as pyplot
import os
import mpl_toolkits.mplot3d as mplot3d
import matplotlib.collections as PolyCollection
import matplotlib.colors as colors

max_freq = 40000.0
scale_log = False
axis = pyplot.subplot(111)

def dBlabel(y, pos):
    if y <= 0.0:
        return "0.0"
    else:
        spl = 20.0 * math.log(y, 10)
        return "%.1f dB" % spl

def log():
    dBformatter = pyplot.FuncFormatter(dBlabel)
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.yaxis.set_major_formatter(dBformatter)
    #	axis.yaxis.set_minor_formatter(dBformatter)
    globals()["scale_log"] = True


def reset_color_cycle():
    cc = axis._get_lines.color_cycle
    while cc.next() != "k":
        pass


def show():
    pyplot.show()
    globals()["axis"] = pyplot.subplot(111)
    if scale_log:
        log()


def _show():
    show()


def plot(data, legend=True, show=True, save=False, name=None, line='-'):
    if not isinstance(data, collections.Iterable):
        data = [data]
    if isinstance(data[0], sumpf.Spectrum):
        log()
        for d in data:
            # create x_data
            x_data = []
            for i in range(len(d)):
                x_data.append(i * d.GetResolution())
            # plot
            for i in range(len(d.GetMagnitude())):
                pyplot.plot(x_data, d.GetMagnitude()[i],line, label=d.GetLabels()[i])
            #				pyplot.plot(x_data[0:len(x_data) // 2], d.GetPhase()[i][0:len(x_data) // 2], label=d.GetLabels()[i])
            #				pyplot.plot(x_data, d.GetGroupDelay()[i], label=d.GetLabels()[i])
        pyplot.xlim((0.0, max_freq))
        axis.set_xlabel("Frequeny [Hz]", fontsize="x-large")
    else:
        for d in data:
            # create x_data
            x_data = []
            for i in range(len(d)):
                x_data.append(float(i) / d.GetSamplingRate())
            # plot
            for i in range(len(d.GetChannels())):
                pyplot.plot(x_data, d.GetChannels()[i], label=d.GetLabels()[i])
        axis.set_xlabel("Time [s]", fontsize="x-large")
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if save is True:
        location = "C:/Users/diplomand.8/OneDrive/Pictures/"
        fig = os.path.join(location,name)
        pyplot.savefig(fig, dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None)
    else:
        if show:
            _show()


def plot_groupdelayandmagnitude(data, legend=True, show=True, save=False, name=None):
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
                ax = pyplot.subplot(2,1,1)
                pyplot.title("Frequency")
                pyplot.loglog(x_data, d.GetMagnitude()[i], label=d.GetLabels()[i])
                pyplot.subplot(2,1,2,sharex=ax)
                pyplot.title("Group delay")
                pyplot.semilogx(x_data, d.GetGroupDelay()[i], label=d.GetLabels()[i])
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if save is True:
        location = "C:/Users/diplomand.8/OneDrive/Pictures/"
        fig = os.path.join(location,name)
        pyplot.savefig(fig, dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None)
    else:
        if show:
            _show()

def plot_timeandfreq(data, legend=True, show=True):
    if isinstance(data,sumpf.Signal):
        data_freq = sumpf.modules.FourierTransform(data).GetSpectrum()
        data_time = data
    elif isinstance(data,sumpf.Spectrum):
        data_time = sumpf.modules.InverseFourierTransform(data).GetSignal()
        data_freq = data
    else:
        print "not sumpf signal or spectrum"
    if not isinstance(data_time, collections.Iterable):
        data_time = [data_time]
    if not isinstance(data_freq, collections.Iterable):
        data_freq = [data_freq]
    for d in data_freq:
        # create x_data
        x_data = []
        for i in range(len(d)):
            x_data.append(i * d.GetResolution())
        # plot
        for i in range(len(d.GetMagnitude())):
            pyplot.subplot(2,1,1)
            pyplot.title("Frequency")
            pyplot.loglog(x_data, d.GetMagnitude()[i], label=d.GetLabels()[i])
    axis.set_xlabel("Frequeny [Hz]", fontsize="x-large")
    for d in data_time:
        # create x_data
        x_data = []
        for i in range(len(d)):
            x_data.append(float(i) / d.GetSamplingRate())
        # plot
        for i in range(len(d.GetChannels())):
            pyplot.subplot(2,1,2)
            pyplot.title("Amplitude")
            pyplot.plot(x_data, d.GetChannels()[i], label=d.GetLabels()[i])
    axis.set_xlabel("Time [s]", fontsize="x-large")
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if show:
        _show()

def relabelandplot(input,label=None,show=True,save=False,name=None,line="-"):
    """
    Relabel the input signal or spectrum and plot
    :param input: the input signal or spectrum
    :param label: the label text
    :param show: True or False
    :return: plots the given input with label
    """
    relabelled = nlsp.relabel(input,label)
    if isinstance(relabelled, sumpf.Spectrum):
        log()
    plot(relabelled,show=show,save=save,name=name,line=line)

def relabelandplotphase(input,label,show=True,save=False,name=None):
    """
    Relabel the input signal or spectrum and plot
    :param input: the input signal or spectrum
    :param label: the label text
    :param show: True or False
    :return: plots the given input with label
    """
    relabelled = nlsp.relabel(input,label)
    if isinstance(relabelled, sumpf.Spectrum):
        log()
    plot_groupdelayandmagnitude(relabelled,show=show)


def plot_array(input_array,label_array=None,save=False,name=None,Show=True):
    """
    Helper function to plot array
    :param input_array: the input array of signal or spectrum
    :param label_array: the array of labels
    :return: the plot of the input array with labels
    """
    if label_array is None:
        label_array = [None,] * len(input_array)
    for input,label in zip(input_array,label_array):
        relabelandplot(input,label,False,save,name)
    if Show is True:
        show()

def plot_filterspec(input_array,show=True):
    for input in input_array:
        input = sumpf.modules.FourierTransform(input).GetSpectrum()
        plot(input,show=False)
    if show is True:
        _show()

def plot_simplearray(x_array,y_array,x_label,y_label,label,show=True):
    # print label
    # fig, ax = pyplot.subplots()
    pyplot.plot(x_array, y_array, label=label)
    pyplot.ylabel(y_label)
    pyplot.xlabel(x_label)
    # Now add the legend with some customizations.
    pyplot.legend(loc='upper center', shadow=True)
    #
    # # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    # frame = legend.get_frame()
    # frame.set_facecolor('0.90')
    #
    # # Set the fontsize
    # for label in legend.get_texts():
    #     label.set_fontsize('large')
    #
    # for label in legend.get_lines():
    #     label.set_linewidth(1.5)  # the legend line width
    if show is True:
        pyplot._show()

def plot_histogram(data, legend=True, show=True, save=False, name=None):
    if not isinstance(data, collections.Iterable):
        data = [data]
    for d in data:
        for i in range(len(d.GetChannels())):
            pyplot.hist(d.GetChannels()[i], bins=500)
    axis.set_xlabel("Value", fontsize="x-large")
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if save is True:
        location = "C:/Users/diplomand.8/OneDrive/Pictures/"
        fig = os.path.join(location,name)
        pyplot.savefig(fig, dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None)
    else:
        if show:
            _show()

def plot_timeandfreq_array(input_array,show=True,legend=True):
    if isinstance(input_array, list) != True:
        array1 = []
        array1.append(input_array)
    else:
        array1 = input_array
    for one in array1:
        if isinstance(one,sumpf.Signal):
            one_signal = one
            one_spectrum = sumpf.modules.FourierTransform(one).GetSpectrum()
        else:
            one_signal = sumpf.modules.InverseFourierTransform(one).GetSignal()
            one_spectrum = one
        plot_timeandfreq(one_signal,one_spectrum,show=False,legend=legend)
    if show is True:
        _show()

def plot_spectrogram(data):
    print
    x_data = []
    for i in range(len(data)):
        x_data.append(float(i) / data.GetSamplingRate())
    y_data = []
    for i in range(len(data.GetSpectrums()[0])):
        y_data.append(i * data.GetSpectrums()[0].GetResolution())
    color_data = []
    for s in data.GetSpectrums():
        color_data.append(s.GetMagnitude()[0])
    color_data = numpy.transpose(color_data)
    axis.set_yscale('symlog')
    axis.set_ylim(y_data[1], y_data[-1])
    axis.set_xlim(x_data[0], x_data[-1])
    x_axis = numpy.array(x_data)
    y_axis = numpy.array(y_data)
    color_grid = numpy.multiply(numpy.log10(color_data), 10.0)
    plot = axis.pcolormesh(x_axis, y_axis, color_grid)
    pyplot.colorbar(plot)
    show()

def plot_sdrvsfreq(input_signalorspectrum,output_signalorspectrum,label=None,show=True):
    if isinstance(input_signalorspectrum, list) != True:
        observed_l = []
        observed_l.append(input_signalorspectrum)
    else:
        observed_l = input_signalorspectrum
    if isinstance(output_signalorspectrum, list) != True:
        identified_l = []
        identified_l.append(output_signalorspectrum)
    else:
        identified_l = output_signalorspectrum
    for observed,identified in zip(observed_l,identified_l):
        if isinstance(observed,(sumpf.Signal,sumpf.Spectrum)) and isinstance(observed,(sumpf.Signal,sumpf.Spectrum)):
            if isinstance(observed,sumpf.Signal):
                observed = sumpf.modules.FourierTransform(observed).GetSpectrum()
            if isinstance(identified,sumpf.Signal):
                identified = sumpf.modules.FourierTransform(identified).GetSpectrum()
            if len(observed) != len(identified):
                merged_spectrum = sumpf.modules.MergeSpectrums(spectrums=[observed,identified],
                                                   on_length_conflict=sumpf.modules.MergeSpectrums.FILL_WITH_ZEROS).GetOutput()
                observed = sumpf.modules.SplitSpectrum(data=merged_spectrum,channels=[0]).GetOutput()
                identified = sumpf.modules.SplitSpectrum(data=merged_spectrum,channels=[1]).GetOutput()

            # observed = nlsp.cut_spectrum(observed,[100,19000])
            # identified = nlsp.cut_spectrum(identified,[100,19000])
            identified = sumpf.modules.InverseFourierTransform(identified).GetSignal()
            observed = sumpf.modules.InverseFourierTransform(observed).GetSignal()
            noise =  identified - observed
            print nlsp.calculateenergy_time(noise)
            if label is None:
                pass
            else:
                noise = nlsp.relabel(noise,labels=label)
            nlsp.common.plots.plot(noise,show=show)
        else:
            print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"

def plot_spectrogram(data):
    f_s = data.GetSamplingRate()
    x = data.GetChannels()[0]
    f, t, Sxx = signal.spectrogram(x,f_s,nperseg=2**11,window=('tukey', 0.1))
    pyplot.pcolormesh(t, f, Sxx)
    pyplot.ylabel('Frequency [Hz]')
    pyplot.xlabel('Time [sec]')
    pyplot.show()