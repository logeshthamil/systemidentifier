import numpy
import itertools
import sumpf
import nlsp

def k_matrix_calculate(input,total_branches):
    """
    Find the k matrix for the input signal
    :param input: the input signal
    :param total_branches: the total number of branches
    :return: the k matrix
    """
    row_array = range(0,total_branches)
    column_array = range(0,total_branches)
    k_matrix = numpy.zeros((total_branches,total_branches))
    for n,m in itertools.product(row_array,column_array):
        n = n + 1
        m = m + 1
        k_matrix[0][0] = 1.000
        if n < m:
            k = 0
            for i in range(n,m):
                num = nlsp.NonlinearFunction.power_series(i+m,input).GetOutput()
                den = nlsp.NonlinearFunction.power_series(2*i,input).GetOutput()
                num = round(sumpf.modules.SignalMean(num).GetMean()[0],3)
                den = round(sumpf.modules.SignalMean(den).GetMean()[0],3)
                k = k + (k_matrix[n-1][i-1]*(num/den))
            k = -round(k,2)
        elif n > m:
            k = 0
        elif n == m:
            k = 1
        if (n+m) % 2 == 1:
            k = 0
        k_matrix[n-1][m-1] = round(k,2)
    return k_matrix


def wgn_hgm_decorrelate(input,total_branches):
    """
    Decorrelate the output signals of the powerseries expansion.
    :param input: the input signal
    :param total_branches: the total number of branches
    :return: the decorrelated signal, the k matrix and the mu matrix
    """
    k_matrix = k_matrix_calculate(input,total_branches)
    mu_matrix = []
    signal_matrix = []
    dummy = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=input.GetSamplingRate(),length=len(input)).GetSignal()
    signal_powers = []
    for i in range(1,total_branches+1,1):
        power = nlsp.NonlinearFunction.power_series(i,input)
        signal_powers.append(power.GetOutput())
    signal_powers_k = []
    k_matrix_t = numpy.transpose(k_matrix)
    for i in range(0,total_branches):
        dummy_sig = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=input.GetSamplingRate(),length=len(input)).GetSignal()
        for sig,k in zip(signal_powers,k_matrix_t[i]):
            sig = sig * k
            dummy_sig = sig + dummy_sig
        signal_powers_k.append(dummy_sig)
    for i in range(0,total_branches):
        core = signal_powers_k[i]
        if i %2 == 0:
            power = nlsp.NonlinearFunction.power_series(i,input)
            mu = sumpf.modules.SignalMean(signal=power.GetOutput()).GetMean()
            mu = sumpf.modules.ConstantSignalGenerator(value=float(mu[0]),samplingrate=core.GetSamplingRate(),length=len(core)).GetSignal()
            mu_matrix.append(sumpf.modules.FourierTransform(mu).GetSpectrum())
            comb = core + mu
        else:
            mu = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=core.GetSamplingRate(),length=len(core)).GetSignal()
            mu_matrix.append(sumpf.modules.FourierTransform(mu).GetSpectrum())
            comb = core
        core = dummy + comb
        signal_matrix.append(core)
    return signal_matrix,k_matrix,mu_matrix

def miso_identification(input_generator, output_wgn, branches):
    """
    MISO approach of system identification.
    :param input_generator: the input generator or the input signal
    :param output_wgn: the response of the nonlinear system
    :param branches: the number of branches
    :return: the filter kernels and the nonlinear function of a HGM
    """
    if hasattr(input_generator,"GetOutput"):
        input_wgn = input_generator.GetOutput()
    else:
        input_wgn = input_generator
    l = []
    L = []
    signal_matrix, k_matrix, mu_matrix = wgn_hgm_decorrelate(input_wgn,branches)
    for branch in range(1,branches+1):
        input_decorrelated = signal_matrix[branch-1]
        cross_corr = sumpf.modules.CorrelateSignals(signal1=input_decorrelated,signal2=output_wgn,mode=sumpf.modules.CorrelateSignals.SPECTRUM).GetOutput()
        num = sumpf.modules.FourierTransform(cross_corr).GetSpectrum()
        den = sumpf.modules.FourierTransform(sumpf.modules.CorrelateSignals(signal1=input_decorrelated,
                                                                            signal2=input_decorrelated,mode=sumpf.modules.CorrelateSignals.SPECTRUM).GetOutput()).GetSpectrum()
        linear = sumpf.modules.DivideSpectrums(spectrum1=num, spectrum2=den).GetOutput()
        kernel = sumpf.modules.InverseFourierTransform(linear).GetSignal()
        signal = sumpf.Signal(channels=kernel.GetChannels(),samplingrate=input_wgn.GetSamplingRate(),labels=kernel.GetLabels())
        l.append(signal)
        L.append(sumpf.modules.FourierTransform(signal).GetSpectrum())
    G = []
    for row in range(0,branches):
        A = sumpf.modules.ConstantSpectrumGenerator(value=0.0,resolution=L[0].GetResolution(),length=len(L[0])).GetSpectrum()
        for column in range(0,branches):
            temp = sumpf.modules.AmplifySpectrum(input=L[column],factor=k_matrix[row][column]).GetOutput()
            A = A + temp
        G.append(sumpf.modules.InverseFourierTransform(A + mu_matrix[row]).GetSignal())
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    return G,nl_func