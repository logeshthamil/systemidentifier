from model_generator import HGMModelGenerator
import sumpf
import nlsp
from nlsp.nonlinear_functions.nonlinear_functions import PolynomialNonlinearBlock
import numpy

class RecomputeFilterKernels(HGMModelGenerator):
    """
    A class to recompute the filter kernels based on the nonlinear function of the HGM.
    """
    def __init__(self, input_model=None, nonlinear_function=None, filter_impulseresponses=None):
        HGMModelGenerator.__init__(self, input_model=input_model, filter_impulseresponses=filter_impulseresponses)
        self.__nonlinear_function = nonlinear_function
        self._FindFilterKernels()

    @sumpf.Input(PolynomialNonlinearBlock, "GetOutputModel")
    def SetNonlinearFunction(self, nonlinearfunction):
        """
        Set the nonlinear function of the HGM.
        @param nonlinearfunction: the nonlinear function Eg, nlsp.nonlinear_function.Power
        """
        self.__nonlinear_function = nonlinearfunction
        self._FindFilterKernels()

    def _FindFilterKernels(self):
        """
        Recompute the filter kernels.
        """
        modify_model = nlsp.ModifyModel(input_model=self._input_model)
        ref_nl = modify_model._nonlinear_functions
        ref_nl_specific = ref_nl[0].__class__
        ref_filter = modify_model._filter_impulseresponses
        degree_nl = []
        self._nonlinear_functions = []
        for nl in ref_nl:
            degree_nl.append(nl.GetMaximumHarmonics())
        if self.__nonlinear_function is None:
            for nl in ref_nl:
                self._nonlinear_functions.append(nl.CreateModified())
            self._filter_impulseresponses = ref_filter
        elif self.__nonlinear_function is ref_nl_specific:
            for nl in ref_nl:
                self._nonlinear_functions.append(nl.CreateModified())
            self._filter_impulseresponses = ref_filter
        elif self.__nonlinear_function is nlsp.nonlinear_function.Power:
            for i in degree_nl:
                self._nonlinear_functions.append(self.__nonlinear_function(degree=i))
            if self.__nonlinear_function is nlsp.nonlinear_function.Chebyshev:
                polynomial = numpy.polynomial.chebyshev.Chebyshev
                coefficient = numpy.polynomial.chebyshev.cheb2poly
                self._filter_impulseresponses = powertoany(degree=degree_nl,ip_filter_kernels=ref_filter,polynomial=polynomial,coefficient=coefficient)
            elif self.__nonlinear_function is nlsp.nonlinear_function.Hermite:
                polynomial = numpy.polynomial.hermite_e.HermiteE
                coefficient = numpy.polynomial.hermite_e.herme2poly
                self._filter_impulseresponses = powertoany(degree=degree_nl,ip_filter_kernels=ref_filter,polynomial=polynomial,coefficient=coefficient)
            elif self.__nonlinear_function is nlsp.nonlinear_function.Legendre:
                polynomial = numpy.polynomial.hermite_e.HermiteE
                coefficient = numpy.polynomial.hermite_e.herme2poly
                self._filter_impulseresponses = powertoany(degree=degree_nl,ip_filter_kernels=ref_filter,polynomial=polynomial,coefficient=coefficient)
        else:
            for i in degree_nl:
                self._nonlinear_functions.append(self.__nonlinear_function(degree=i))
            if self.__nonlinear_function is nlsp.nonlinear_function.Chebyshev:
                polynomial = numpy.polynomial.chebyshev.Chebyshev
                coefficient = numpy.polynomial.chebyshev.cheb2poly
                temp = anytopower(degree=degree_nl,ip_filter_kernels=ref_filter,polynomial=polynomial,coefficient=coefficient)
                self._filter_impulseresponses = powertoany(degree=degree_nl,ip_filter_kernels=temp,polynomial=polynomial,coefficient=coefficient)
            elif self.__nonlinear_function is nlsp.nonlinear_function.Hermite:
                polynomial = numpy.polynomial.hermite_e.HermiteE
                coefficient = numpy.polynomial.hermite_e.herme2poly
                temp = anytopower(degree=degree_nl,ip_filter_kernels=ref_filter,polynomial=polynomial,coefficient=coefficient)
                self._filter_impulseresponses = powertoany(degree=degree_nl,ip_filter_kernels=temp,polynomial=polynomial,coefficient=coefficient)
            elif self.__nonlinear_function is nlsp.nonlinear_function.Legendre:
                polynomial = numpy.polynomial.legendre.Legendre
                coefficient = numpy.polynomial.legendre.leg2poly
                temp = anytopower(degree=degree_nl,ip_filter_kernels=ref_filter,polynomial=polynomial,coefficient=coefficient)
                self._filter_impulseresponses = powertoany(degree=degree_nl,ip_filter_kernels=temp,polynomial=polynomial,coefficient=coefficient)

def powertoany(degree,ip_filter_kernels,polynomial,coefficient):
    ip_filter_kernels_spec = []
    for kernel in ip_filter_kernels:
        ip_filter_kernels_spec.append(sumpf.modules.FourierTransform(kernel).GetSpectrum())
    degree.insert(0,0)
    op_filter_kernels_s = []
    coefficients = []
    for d in degree:
        temp = [0,]*(d)
        temp.append(1)
        poly = polynomial(temp)
        coef = coefficient(poly.coef)
        coeff = numpy.append(coef,[0,]*(max(degree)+1-len(coef)))
        coefficients.append(coeff)
    coefficients = numpy.asarray(coefficients)
    coefficients = numpy.transpose(coefficients)
    coefficients = numpy.linalg.inv(coefficients)
    coefficients = numpy.delete(coefficients, numpy.s_[::len(degree)], 1)
    constants = numpy.transpose(coefficients[0])
    coefficients = coefficients[1:]
    constant_specs = []
    for i,c in enumerate(constants):
        constant_signal = sumpf.modules.ImpulseGenerator(samplingrate=ip_filter_kernels[0].GetSamplingRate(), length=len(ip_filter_kernels[0])).GetSignal()*c
        constant_spec = sumpf.modules.FourierTransform(constant_signal).GetSpectrum()
        constant_spec = constant_spec * ip_filter_kernels_spec[i]
        constant_specs.append(constant_spec)
    ip_sub = []
    for spec, cons in zip(ip_filter_kernels_spec,constant_specs):
        sub = sumpf.modules.Subtract(value1=spec, value2=cons).GetResult()
        ip_sub.append(sub)
    for coeff in coefficients:
        product = []
        for i in range(len(coeff)):
            product.append(ip_sub[i]*coeff[i])
        filter_kernel = sum(product)
        op_filter_kernels_s.append(sumpf.modules.InverseFourierTransform(filter_kernel).GetSignal())
    return op_filter_kernels_s


def anytopower(degree=None,ip_filter_kernels=None,polynomial=None,coefficient=None):
    ip_filter_kernels_spec = []
    for kernel in ip_filter_kernels:
        ip_filter_kernels_spec.append(sumpf.modules.FourierTransform(kernel).GetSpectrum())
    degree_temp = numpy.insert(degree,0,0)
    op_filter_kernels_s = []
    coefficients = []
    for d in degree_temp:
        temp = [0,]*(d)
        temp.append(1)
        poly = polynomial(temp)
        coef = coefficient(poly.coef)
        coeff = numpy.append(coef,[0,]*(max(degree_temp)+1-len(coef)))
        coefficients.append(coeff)
    coefficients = numpy.asarray(coefficients)
    coefficients = numpy.transpose(coefficients)
    # coefficients = numpy.linalg.inv(coefficients)
    coefficients = numpy.delete(coefficients, numpy.s_[::len(degree_temp)], 1)
    constants = numpy.transpose(coefficients[0])
    coefficients = coefficients[1:]
    constant_specs = []
    for i,c in enumerate(constants):
        constant_signal = sumpf.modules.ImpulseGenerator(samplingrate=ip_filter_kernels[0].GetSamplingRate(), length=len(ip_filter_kernels[0])).GetSignal()*c
        constant_spec = sumpf.modules.FourierTransform(constant_signal).GetSpectrum()
        constant_spec = constant_spec * ip_filter_kernels_spec[i]
        constant_specs.append(constant_spec)
    for coeff in coefficients:
        product = []
        for i in range(len(coeff)):
            product.append(ip_filter_kernels_spec[i]*coeff[i])
        filter_kernel = sum(product)
        op_filter_kernels_s.append(filter_kernel)
    op_filters = []
    for spec,cons in zip(op_filter_kernels_s,constant_specs):
        op = sumpf.modules.Add(value1=spec,value2=cons).GetResult()
        op_filters.append(sumpf.modules.InverseFourierTransform(op).GetSignal())
    return op_filters
