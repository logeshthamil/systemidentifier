import sumpf
import nlsp
import numpy
import scipy.optimize
import pandas


def compute_iir_from_fir_using_curvetracing_biquads(fir_kernels=None, algorithm='Nelder-Mead', initial_coeff=None,
                                                    filter_order=4,
                                                    start_freq=50.0, stop_freq=19000.0, Print=True, max_iterations=1000,
                                                    plot_individual=False, return_error=False, return_coeffs=False):
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
    pandas.DataFrame()
    coefficients = []
    frequencies = []
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
        positive_cut = nlsp.common.helper_functions_private.cut_spectrum(input_spectrum=positive,
                                                                         desired_frequency_range=[start_freq,
                                                                                                  stop_freq])
        # error and exponential error calculation
        errorexp = nlsp.common.helper_functions_private.exponentially_weighted_sum(positive_cut)[0]
        error = numpy.sum(positive_cut.GetChannels()[0])

        # variance calculation
        distance = difference - sumpf.modules.SpectrumMean(spectrum=difference).GetMean()
        distance_square = sumpf.modules.Multiply(value1=distance, value2=distance).GetResult()
        sum = numpy.sum(distance_square.GetChannels()[0])
        variance = sum / len(distance_square.GetChannels()[0])

        # mean calculation
        mean = abs(numpy.mean(nlsp.common.helper_functions_private.cut_spectrum(positive,
                                                                                desired_frequency_range=[start_freq,
                                                                                                         stop_freq]).GetChannels()))

        # error value calculation
        error_value = abs(mean * 100 + error + errorexp + variance * 100)
        if return_error is True:
            Error.append(error_value)
        if Print is True:
            print "Error value:" + str(error_value)
        return error_value

    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(signal=fir_kernels[0])
    if initial_coeff is None:
        initial_coeff = sumpf.modules.FilterGenerator.BUTTERWORTH(order=filter_order).GetCoefficients()
        iir_initial = [initial_coeff, ] * len(fir_kernels)
        freq = [1000.0, ] * len(fir_kernels)
    else:
        iir_initial = initial_coeff.coefficients
        freq = initial_coeff.frequencies
    for fir_individual, iir_individual, frequen in zip(fir_kernels, iir_initial, freq):  # each filter adaptation
        fir_individual = sumpf.modules.FourierTransform(fir_individual).GetSpectrum()
        coeffs = []
        for biquad_n in range(len(iir_individual)):
            num = iir_individual[biquad_n][0]
            num = numpy.asarray(num)
            num = numpy.append(num, [1, ] * (3 - len(num)), axis=0)
            den = iir_individual[biquad_n][1]
            coeffs.append(num)
            coeffs.append(den)
        coeffs = numpy.concatenate(numpy.array(coeffs), axis=0)
        coeffs = numpy.append(coeffs, [frequen], axis=0)
        Error = []
        print "Initial Coefficients:" + str(coeffs)
        result = scipy.optimize.minimize(errorfunction, (coeffs), method=algorithm,
                                         options={'disp': False, 'maxiter': max_iterations})
        iden_filter = sumpf.modules.ConstantSpectrumGenerator(value=1.0, resolution=prp.GetResolution(),
                                                              length=prp.GetSpectrumLength()).GetSpectrum()
        individual_coeff = []
        for a, b, c, d, e, f in zip(*[iter(result.x)] * 6):
            num = [a, b, c]
            den = [d, e, f]
            individual_coeff.append([num, den])
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
        if return_coeffs is True:
            coefficients.append(individual_coeff)
            frequencies.append(result.x[-1])
    all_coeff = pandas.Series([coefficients, frequencies], index=['coefficients', 'frequencies'])
    return iir_identified, Error, all_coeff


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
        positive_cut = nlsp.common.helper_functions_private.cut_spectrum(input_spectrum=positive,
                                                                         desired_frequency_range=[start_freq,
                                                                                                  stop_freq])
        # error and exponential error calculation
        errorexp = nlsp.common.helper_functions_private.exponentially_weighted_sum(positive_cut)[0]
        error = numpy.sum(positive_cut.GetChannels()[0])

        # variance calculation
        distance = difference - sumpf.modules.SpectrumMean(spectrum=difference).GetMean()
        distance_square = sumpf.modules.Multiply(value1=distance, value2=distance).GetResult()
        sum = numpy.sum(distance_square.GetChannels()[0])
        variance = sum / len(distance_square.GetChannels()[0])

        # mean calculation
        mean = abs(numpy.mean(nlsp.common.helper_functions_private.cut_spectrum(positive,
                                                                                desired_frequency_range=[start_freq,
                                                                                                         stop_freq]).GetChannels()))

        # error value calculation
        error_value = abs(mean * 100 + error + errorexp + variance * 100)
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
    return iir_identified, Error


def compute_iir_from_fir_using_curvetracing_sequencialbiquads(fir_kernels=None, algorithm='Nelder-Mead',
                                                              filter_order=4, start_freq=50.0, stop_freq=19000.0,
                                                              Print=True,
                                                              max_iterations=1000, plot_individual=False,
                                                              return_error=False):
    """
    Compute the equivalent iir biquad filter kernels sequencially for fir filters.

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
    found_iir = []
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(signal=fir_kernels[0])
    for fir_individual in fir_kernels:  # each filter adaptation
        individual_biquad = None
        for filt_ord in range(2, filter_order + 1, 2):
            found_biquad, error, coeffs = compute_iir_from_fir_using_curvetracing_biquads(
                fir_kernels=[fir_individual, ], algorithm=algorithm, initial_coeff=individual_biquad,
                filter_order=filt_ord, start_freq=start_freq, stop_freq=stop_freq,
                Print=True, max_iterations=max_iterations, plot_individual=False,
                return_error=return_error, return_coeffs=True)
            temp_coeff = sumpf.modules.FilterGenerator.BUTTERWORTH(order=filter_order).GetCoefficients()[0]
            coeffs.coefficients[0].append(temp_coeff)
            individual_biquad = coeffs
        if plot_individual is True:
            nlsp.plots.plot(sumpf.modules.FourierTransform(found_biquad[0]).GetSpectrum(), show=False)
            nlsp.plots.plot(sumpf.modules.FourierTransform(fir_individual).GetSpectrum())
        found_iir.append(found_biquad)
    return found_iir
