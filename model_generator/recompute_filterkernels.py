import numpy
import sumpf


def powertoany(degree, ip_filter_kernels, polynomial, coefficient):
    """
    Convert the filter coefficients from the powerseries expansion nonlinear function to any.

    :param degree: the degree of the nonlinear functions
    :param ip_filter_kernels: the reference filter kernels
    :param polynomial: the desired polynomial function
    :param coefficient: the desired polynomial coefficients
    """
    ip_filter_kernels_spec = []
    for kernel in ip_filter_kernels:
        ip_filter_kernels_spec.append(sumpf.modules.FourierTransform(kernel).GetSpectrum())
    degree.insert(0, 0)
    op_filter_kernels_s = []
    coefficients = []
    for d in degree:
        temp = [0, ] * (d)
        temp.append(1)
        poly = polynomial(temp)
        coef = coefficient(poly.coef)
        coeff = numpy.append(coef, [0, ] * (max(degree) + 1 - len(coef)))
        coefficients.append(coeff)
    coefficients = numpy.asarray(coefficients)
    coefficients = numpy.transpose(coefficients)
    coefficients = numpy.linalg.inv(coefficients)
    coefficients = numpy.delete(coefficients, numpy.s_[::len(degree)], 1)
    constants = numpy.transpose(coefficients[0])
    coefficients = coefficients[1:]
    constant_specs = []
    for i, c in enumerate(constants):
        constant_signal = sumpf.modules.ImpulseGenerator(samplingrate=ip_filter_kernels[0].GetSamplingRate(),
                                                         length=len(ip_filter_kernels[0])).GetSignal() * c
        constant_spec = sumpf.modules.FourierTransform(constant_signal).GetSpectrum()
        constant_spec = constant_spec * ip_filter_kernels_spec[i]
        constant_specs.append(constant_spec)
    ip_sub = []
    for spec, cons in zip(ip_filter_kernels_spec, constant_specs):
        sub = sumpf.modules.Subtract(value1=spec, value2=cons).GetResult()
        ip_sub.append(sub)
    for coeff in coefficients:
        product = []
        for i in range(len(coeff)):
            product.append(ip_sub[i] * coeff[i])
        filter_kernel = sum(product)
        op_filter_kernels_s.append(sumpf.modules.InverseFourierTransform(filter_kernel).GetSignal())
    return op_filter_kernels_s


def anytopower(degree=None, ip_filter_kernels=None, polynomial=None, coefficient=None):
    """
    Convert the filter coefficients from any nonlinear function other than powerseries expansion.

    :param degree: the degree of the nonlinear functions
    :param ip_filter_kernels: the reference filter kernels
    :param polynomial: the desired polynomial function
    :param coefficient: the desired polynomial coefficients
    """
    ip_filter_kernels_spec = []
    for kernel in ip_filter_kernels:
        ip_filter_kernels_spec.append(sumpf.modules.FourierTransform(kernel).GetSpectrum())
    degree_temp = numpy.insert(degree, 0, 0)
    op_filter_kernels_s = []
    coefficients = []
    for d in degree_temp:
        temp = [0, ] * (d)
        temp.append(1)
        poly = polynomial(temp)
        coef = coefficient(poly.coef)
        coeff = numpy.append(coef, [0, ] * (max(degree_temp) + 1 - len(coef)))
        coefficients.append(coeff)
    coefficients = numpy.asarray(coefficients)
    coefficients = numpy.transpose(coefficients)
    # coefficients = numpy.linalg.inv(coefficients)
    coefficients = numpy.delete(coefficients, numpy.s_[::len(degree_temp)], 1)
    constants = numpy.transpose(coefficients[0])
    coefficients = coefficients[1:]
    constant_specs = []
    for i, c in enumerate(constants):
        constant_signal = sumpf.modules.ImpulseGenerator(samplingrate=ip_filter_kernels[0].GetSamplingRate(),
                                                         length=len(ip_filter_kernels[0])).GetSignal() * c
        constant_spec = sumpf.modules.FourierTransform(constant_signal).GetSpectrum()
        constant_spec = constant_spec * ip_filter_kernels_spec[i]
        constant_specs.append(constant_spec)
    for coeff in coefficients:
        product = []
        for i in range(len(coeff)):
            product.append(ip_filter_kernels_spec[i] * coeff[i])
        filter_kernel = sum(product)
        op_filter_kernels_s.append(filter_kernel)
    op_filters = []
    for spec, cons in zip(op_filter_kernels_s, constant_specs):
        op = sumpf.modules.Add(value1=spec, value2=cons).GetResult()
        op_filters.append(sumpf.modules.InverseFourierTransform(op).GetSignal())
    return op_filters
