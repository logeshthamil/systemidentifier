import sumpf
import nlsp
import numpy
import scipy.optimize
import pandas


def compute_iir_from_fir_using_curvetracing_biquads(fir_kernels=None, algorithm='Nelder-Mead', initial_coeff=None,
                                                    filter_order=4, start_freq=50.0, stop_freq=19000.0, Print=True,
                                                    max_iterations=1000, plot_individual=False):
    iir_identified = []
    coefficients = []
    frequencies = []

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
        # exponential error calculation
        errorexp1 = nlsp.common.helper_functions_private.calculateenergy_freqdomain(
            nlsp.common.helper_functions_private.exponential_weighting(positive_cut, base=1.1))[0]
        errorexp2 = nlsp.common.helper_functions_private.exponentially_weighted_sum(positive_cut)[0]
        error_value = errorexp2
        if Print is True:
            print "Error value:" + str(error_value)
        return error_value

    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(signal=fir_kernels[0])
    if initial_coeff is None:
        initial_coeff = sumpf.modules.FilterGenerator.BUTTERWORTH(order=filter_order).GetCoefficients()
        # initial_coeff = [([1.0, 1.0, 1.0], [1.0, 1.0, 1.0]),]*(filter_order/2)
        iir_initial = [initial_coeff, ] * len(fir_kernels)
        freq = [1000.0, ] * len(fir_kernels)
    else:
        iir_initial = initial_coeff.coefficients
        freq = initial_coeff.frequencies
    for fir_individual, iir_individual, frequen in zip(fir_kernels, iir_initial, freq):  # each filter adaptation
        factor = 1
        while (nlsp.common.helper_functions_private.calculateenergy_freqdomain(fir_individual * factor)[0] < 900):
            factor = factor + 1
        fir_individual = sumpf.modules.FourierTransform(fir_individual * factor).GetSpectrum()
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
        if Print is True:
            print "Initial Coefficients:" + str(coeffs)
        result = scipy.optimize.minimize(errorfunction, (coeffs), method=algorithm,
                                         options={'disp': False, 'maxiter': max_iterations})
        iden_filter = sumpf.modules.ConstantSpectrumGenerator(value=1.0, resolution=prp.GetResolution(),
                                                              length=prp.GetSpectrumLength()).GetSpectrum()
        individual_coeff = []
        for a, b, c, d, e, f in zip(*[iter(result.x)] * 6):
            num = [a, b, c]
            den = [d, e, f]
            num = numpy.asarray(num)
            num = num / factor
            individual_coeff.append([num, den])
            temp = sumpf.modules.FilterGenerator(
                filterfunction=sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=num, denominator=den),
                length=prp.GetSpectrumLength(), resolution=prp.GetResolution(),
                frequency=result.x[-1]).GetSpectrum()
            iden_filter = iden_filter * temp
        if Print is True:
            print "Initial coefficients" + str(coeffs)
            print "Final coefficients" + str(result.x)
        if plot_individual is True:
            nlsp.plot.plot_signalorspectrum(iden_filter, show=False)
            nlsp.plot.plot_signalorspectrum(fir_individual, show=True)
        iir_identified.append(sumpf.modules.InverseFourierTransform(iden_filter).GetSignal())
        coefficients.append(individual_coeff)
        frequencies.append(result.x[-1])
    all_coeff = pandas.Series([coefficients, frequencies], index=['coefficients', 'frequencies'])
    return iir_identified, all_coeff


def compute_iir_from_fir_using_curvetracing_higherorder(fir_kernels=None, algorithm='Powell', initial_coeff=None,
                                                        filter_order=4, start_freq=50.0, stop_freq=19000.0, Print=True,
                                                        max_iterations=100, plot_individual=False):
    iir_identified = []
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(signal=fir_kernels[0])
    coefficients = []
    frequencies = []

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
        # exponential error calculation
        errorexp1 = nlsp.common.helper_functions_private.calculateenergy_freqdomain(
            nlsp.common.helper_functions_private.exponential_weighting(positive_cut, base=1.1))[0]
        errorexp2 = nlsp.common.helper_functions_private.exponentially_weighted_sum(positive_cut)[0]
        error_value = errorexp2
        if Print is True:
            print "Error value:" + str(error_value)
        return error_value

    if initial_coeff is None:
        num = numpy.ones(filter_order + 1)
        den = numpy.ones(filter_order + 1)
        iir_initial = [[num, den], ] * len(fir_kernels)
        freq = [1000.0, ] * len(fir_kernels)
    else:
        iir_initial = initial_coeff.coefficients
        freq = initial_coeff.frequencies

    for fir_individual, iir_individual, frequen in zip(fir_kernels, iir_initial, freq):  # each filter adaptation
        factor = 1
        while (nlsp.common.helper_functions_private.calculateenergy_freqdomain(fir_individual * factor)[0] < 900):
            factor = factor + 1
        fir_individual = sumpf.modules.FourierTransform(fir_individual * factor).GetSpectrum()
        coeffs = []
        num = iir_individual[0]
        den = iir_individual[1]
        coeffs.append(num)
        coeffs.append(den)
        coeffs = numpy.concatenate(coeffs, axis=0)
        coeffs = numpy.append(coeffs, [frequen], axis=0)
        result = scipy.optimize.minimize(errorfunction, (coeffs), method=algorithm,
                                         options={'disp': False, 'maxiter': max_iterations})
        freq_param = result.x[-1]
        num = numpy.array(result.x[:(len(result.x) - 1) / 2])
        num = num / factor
        den = numpy.array(result.x[(len(result.x) - 1) / 2:-1])
        iden_filter = sumpf.modules.FilterGenerator(
            filterfunction=sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=num, denominator=den),
            length=prp.GetSpectrumLength(), resolution=prp.GetResolution(), frequency=freq_param).GetSpectrum()
        if Print is True:
            print "Initial coefficients" + str(coeffs)
            print "Final coefficients" + str(result.x)
        if plot_individual is True:
            nlsp.plot.plot_signalorspectrum(iden_filter, show=False)
            nlsp.plot.plot_signalorspectrum(fir_individual / factor, show=True)
        iir_identified.append(sumpf.modules.InverseFourierTransform(iden_filter).GetSignal())
        coefficients.append([num, den])
        frequencies.append(result.x[-1])
    all_coeff = pandas.Series([coefficients, frequencies], index=['coefficients', 'frequencies'])
    return iir_identified, all_coeff

# def compute_iir_from_fir_using_curvetracing_sequencialbiquads(fir_kernels=None, algorithm='Nelder-Mead',
#                                                               filter_order=4, start_freq=50.0, stop_freq=19000.0,
#                                                               Print=True, max_iterations=1000, plot_individual=False):
#     found_iir = []
#     individual_biquad = None
#     prp = sumpf.modules.ChannelDataProperties()
#     prp.SetSignal(signal=fir_kernels[0])
#     for fir_individual in fir_kernels:  # each filter adaptation
#         individual_biquad = None
#         for filt_ord in range(2, filter_order + 1, 2):
#             found_biquad, coeffs = compute_iir_from_fir_using_curvetracing_biquads(
#                 fir_kernels=[fir_individual, ], algorithm=algorithm, initial_coeff=individual_biquad,
#                 filter_order=filt_ord, start_freq=start_freq, stop_freq=stop_freq,
#                 Print=Print, max_iterations=max_iterations, plot_individual=False)
#             temp_coeff = sumpf.modules.FilterGenerator.BUTTERWORTH(order=filter_order).GetCoefficients()[0]
#             coeffs.coefficients[0].append(temp_coeff)
#             individual_biquad = coeffs
#         if plot_individual is True:
#             nlsp.plots.plot(sumpf.modules.FourierTransform(found_biquad[0]).GetSpectrum(), show=False)
#             nlsp.plots.plot(sumpf.modules.FourierTransform(fir_individual).GetSpectrum())
#         found_iir.append(found_biquad)
#     return found_iir
