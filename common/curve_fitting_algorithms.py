import sumpf
import nlsp
import numpy
import scipy.optimize


def compute_iir_from_fir_using_curvetracing_biquads(fir_kernels=None, algorithm='Nelder-Mead', initial_coeff=None,
                                                    filter_order=4,
                                                    start_freq=50.0, stop_freq=19000.0, Print=True, max_iterations=1000,
                                                    plot_individual=False, return_error=False):
    """
    Compute the equivalent iir biquad filter kernels for fir filters.

    :param fir_kernels: the fir filter kernels
    :type fir_kernels: array of sumpf.Signal()
    :param algorithm: the curve tracing algorithm Eg, 'Nelder-Mead', 'Powell', 'BFGS', 'CG' etc,
    :type algorithm: scipy.optimize.minimize(), method parameter
    :param initial_coeff: the initial iir filter coefficients
    :type initial_coeff: array of sumpf.modules.FilterGenerator.BUTTERWORTH(order=100).GetCoefficients()
    :param filter_order: the order of the iir filter
    :type filter_order: int
    :param start_freq: the starting desired frequency
    :type start_freq: float
    :param stop_freq: the stoping desired frequency
    :type stop_freq: float
    :return: the iir filter kernels
    :rtype: array of sumpf.Signal()
    """
    iir_identified = []

    # freq_unique = (2.0 * numpy.pi)
    def errorfunction(parameters):
        iden_filter = sumpf.modules.ConstantSpectrumGenerator(value=1.0, resolution=prp.GetResolution(),
                                                              length=prp.GetSpectrumLength()).GetSpectrum()
        for a, b, c, d, e, f in zip(*[iter(parameters)] * 6):
            num = [a, b, c]
            den = [d, e, f]
            temp = sumpf.modules.FilterGenerator(
                filterfunction=sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=num, denominator=den),
                length=prp.GetSpectrumLength(), resolution=prp.GetResolution(),
                frequency=parameters[-1]).GetSpectrum()
            iden_filter = iden_filter * temp
        difference = iden_filter - fir_individual
        positive = difference * difference
        magnitude = numpy.array(positive.GetMagnitude())
        cropped = magnitude[:,
                  int(round(start_freq / positive.GetResolution())):int(round(stop_freq / positive.GetResolution()))]
        exp = numpy.exp(cropped)
        errorexp = numpy.sum(exp)
        error = numpy.sum(cropped)
        mean = abs(numpy.mean(nlsp.common.helper_functions_private.cut_spectrum(positive,
                                                                                desired_frequency_range=[start_freq,
                                                                                                         stop_freq]).GetChannels()))
        error_value = mean * 100 + error + errorexp
        if Print is True:
            print "Error value:" + str(error_value)
        if return_error is True:
            Error.append(error_value)
        return error_value

    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(signal=fir_kernels[0])
    if initial_coeff is None:
        initial_coeff = sumpf.modules.FilterGenerator.BUTTERWORTH(order=filter_order).GetCoefficients()
        print "Initial Coefficients:" + str(initial_coeff)
        iir_initial = [initial_coeff, ] * len(fir_kernels)
    else:
        iir_initial = initial_coeff
    for fir_individual, iir_individual in zip(fir_kernels, iir_initial):  # each filter adaptation
        fir_individual = sumpf.modules.FourierTransform(fir_individual).GetSpectrum()
        coeffs = []
        for biquad_n in range(len(iir_individual)):
            num = iir_individual[biquad_n][0]
            num = numpy.asarray(num)
            num = numpy.append(num, [0, 0], axis=0)
            den = iir_individual[biquad_n][1]
            coeffs.append(num)
            coeffs.append(den)
        coeffs = numpy.concatenate(numpy.array(coeffs), axis=0)
        coeffs = numpy.append(coeffs, [1000.0], axis=0)
        Error = []
        result = scipy.optimize.minimize(errorfunction, (coeffs), method=algorithm,
                                         options={'disp': False, 'maxiter': max_iterations})
        iden_filter = sumpf.modules.ConstantSpectrumGenerator(value=1.0, resolution=prp.GetResolution(),
                                                              length=prp.GetSpectrumLength()).GetSpectrum()
        for a, b, c, d, e, f in zip(*[iter(result.x)] * 6):
            num = [a, b, c]
            den = [d, e, f]
            temp = sumpf.modules.FilterGenerator(
                filterfunction=sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=num, denominator=den),
                length=prp.GetSpectrumLength(), resolution=prp.GetResolution(),
                frequency=result.x[-1]).GetSpectrum()
            iden_filter = iden_filter * temp
        print "Initial coefficients" + str(coeffs)
        print "Final coefficients" + str(result.x)
        if plot_individual is True:
            nlsp.plots.plot(iden_filter, show=False)
            nlsp.plots.plot(fir_individual, show=True)
        iir_identified.append(sumpf.modules.InverseFourierTransform(iden_filter).GetSignal())
        if return_error is True:
            Error = numpy.asarray(Error)
            Error[Error > 50000] = 50000
        else:
            Error = None
    return iir_identified, Error


def compute_iir_from_fir_using_curvetracing_higherorder(fir_kernels=None, algorithm='Nelder-Mead', initial_coeff=None,
                                                        filter_order=4,
                                                        start_freq=50.0, stop_freq=19000.0, Print=True,
                                                        max_iterations=100,
                                                        plot_individual=False, return_error=False):
    """
    Compute the equivalent higher order iir filter kernels for fir filters.

    :param fir_kernels: the fir filter kernels
    :type fir_kernels: array of sumpf.Signal()
    :param algorithm: the curve tracing algorithm Eg, 'Nelder-Mead', 'Powell', 'BFGS', 'CG' etc,
    :type algorithm: scipy.optimize.minimize(), method parameter
    :param initial_coeff: the initial iir filter coefficients
    :type initial_coeff: array of sumpf.modules.FilterGenerator.BUTTERWORTH(order=100).GetCoefficients()
    :param filter_order: the order of the iir filter
    :type filter_order: int
    :param start_freq: the starting desired frequency
    :type start_freq: float
    :param stop_freq: the stoping desired frequency
    :type stop_freq: float
    :return: the iir filter kernels
    :rtype: array of sumpf.Signal()
    """
    iir_identified = []
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(signal=fir_kernels[0])

    def errorfunction(parameters):
        freq_param = parameters[-1]
        num = parameters[:(len(parameters) - 1) / 2]
        den = parameters[(len(parameters) - 1) / 2:-1]
        iden_filter = sumpf.modules.FilterGenerator(
            filterfunction=sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=num, denominator=den),
            length=prp.GetSpectrumLength(), resolution=prp.GetResolution(), frequency=freq_param).GetSpectrum()
        difference = iden_filter - fir_individual
        positive = difference * difference
        magnitude = numpy.array(positive.GetMagnitude())
        cropped = magnitude[:,
                  int(round(start_freq / positive.GetResolution())):int(round(stop_freq / positive.GetResolution()))]
        exp = numpy.exp(cropped)
        errorexp = numpy.sum(exp)
        error = numpy.sum(cropped)
        mean = abs(numpy.mean(nlsp.common.helper_functions_private.cut_spectrum(positive,
                                                                                desired_frequency_range=[start_freq,
                                                                                                         stop_freq]).GetChannels()))
        error_value = mean * 100 + error + errorexp
        if return_error is True:
            Error.append(error_value)
        if Print is True:
            print "Error value:" + str(error_value)
        return error_value

    if initial_coeff is None:
        num = numpy.ones(filter_order + 1)
        den = numpy.ones(filter_order + 1)
        iir_initial = [[num, den], ] * len(fir_kernels)
    else:
        iir_initial = initial_coeff
    iir_initial = numpy.asarray(iir_initial)
    for fir_individual, iir_individual in zip(fir_kernels, iir_initial):  # each filter adaptation
        fir_individual = sumpf.modules.FourierTransform(fir_individual).GetSpectrum()
        coeffs = []
        num = iir_individual[0]
        den = iir_individual[1]
        coeffs.append(num)
        coeffs.append(den)
        coeffs = numpy.concatenate(coeffs, axis=0)
        coeffs = numpy.append(coeffs, [1000.0], axis=0)
        Error = []
        result = scipy.optimize.minimize(errorfunction, (coeffs), method=algorithm,
                                         options={'disp': False, 'maxiter': max_iterations})
        freq_param = result.x[-1]
        num = result.x[:(len(result.x) - 1) / 2]
        den = result.x[(len(result.x) - 1) / 2:-1]
        iden_filter = sumpf.modules.FilterGenerator(
            filterfunction=sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=num, denominator=den),
            length=prp.GetSpectrumLength(), resolution=prp.GetResolution(), frequency=freq_param).GetSpectrum()
        print "Initial coefficients" + str(coeffs)
        print "Final coefficients" + str(result.x)
        if plot_individual is True:
            nlsp.plots.plot(iden_filter, show=False)
            nlsp.plots.plot(fir_individual, show=True)
        iir_identified.append(sumpf.modules.InverseFourierTransform(iden_filter).GetSignal())
        if return_error is True:
            Error = numpy.asarray(Error)
            Error[Error > 50000] = 50000
        else:
            Error = None
    return iir_identified
