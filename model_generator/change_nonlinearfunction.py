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
        ref_filter = modify_model._filter_impulseresponses
        degree = []
        self._nonlinear_functions = []
        for nl in ref_nl:
            degree.append(nl.GetMaximumHarmonics())
        if self.__nonlinear_function is None:
            for nl in ref_nl:
                self._nonlinear_functions.append(nl.CreateModified())
            self._filter_impulseresponses = ref_filter
        else:
            for i in degree:
                self._nonlinear_functions.append(self.__nonlinear_function(degree=i))
            if self.__nonlinear_function is nlsp.nonlinear_function.Power:
                print "power"
                polynomial = numpy.polynomial.hermite.Hermite
                coefficient = numpy.polynomial.hermite.herm2poly
                self._filter_impulseresponses = anytopower(degree=degree,ip_filter_kernels=ref_filter,polynomial=polynomial,coefficient=coefficient)
            elif self.__nonlinear_function is nlsp.nonlinear_function.Chebyshev:
                print "cheby"
                polynomial = numpy.polynomial.chebyshev.Chebyshev
                coefficient = numpy.polynomial.chebyshev.cheb2poly
                self._filter_impulseresponses = anytopower(degree=degree,ip_filter_kernels=ref_filter,polynomial=polynomial,coefficient=coefficient)
            elif self.__nonlinear_function is nlsp.nonlinear_function.Hermite:
                print "hermite"
                polynomial = numpy.polynomial.hermite_e.HermiteE
                coefficient = numpy.polynomial.hermite_e.herme2poly
                self._filter_impulseresponses = anytopower(degree=degree,ip_filter_kernels=ref_filter,polynomial=polynomial,coefficient=coefficient)
            elif self.__nonlinear_function is nlsp.nonlinear_function.Legendre:
                print "legendre"

def powertoany(degree,ip_filter_kernels,polynomial,coefficient):
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
    coefficients = numpy.delete(coefficients, numpy.s_[::len(degree)], 1)
    constants = numpy.transpose(coefficients[0])
    coefficients = coefficients[1:]
    coefficients_i = numpy.linalg.inv(coefficients)
    c = []
    constant_specs = []
    for i in constants:
        constant_signal = sumpf.modules.ConstantSignalGenerator(value=i,samplingrate=ip_filter_kernels[0].GetSamplingRate(),
                                                                length=len(ip_filter_kernels[0])).GetSignal()
        constant_spec = sumpf.modules.FourierTransform(constant_signal).GetSpectrum()
        constant_specs.append(constant_spec)
    ip_filter_kernels_modif = []
    for kernel, cons in zip(ip_filter_kernels,constant_specs):
        sub = sumpf.modules.Subtract(value1=sumpf.modules.FourierTransform(kernel).GetSpectrum(), value2=cons).GetResult()
        ip_filter_kernels_modif.append(sub)
    for coeff in coefficients_i:
        c.append(coeff)
        product = []
        for i in range(len(coeff)):
            product.append(ip_filter_kernels_modif[i]*coeff[i])
        filter_kernel = sum(product)
        op_filter_kernels_s.append(sumpf.modules.InverseFourierTransform(filter_kernel).GetSignal())
    return op_filter_kernels_s

def anytopower(degree,ip_filter_kernels,polynomial,coefficient):
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
    coefficients = numpy.delete(coefficients, numpy.s_[::len(degree)], 1)
    constants = numpy.transpose(coefficients[0])
    coefficients = coefficients[1:]
    c = []
    constant_specs = []
    for i in constants:
        constant_signal = sumpf.modules.ConstantSignalGenerator(value=i,samplingrate=ip_filter_kernels[0].GetSamplingRate(),
                                                                length=len(ip_filter_kernels[0])).GetSignal()
        constant_spec = sumpf.modules.FourierTransform(constant_signal).GetSpectrum()
        constant_specs.append(constant_spec)
    for coeff in coefficients:
        c.append(coeff)
        product = []
        for i in range(len(coeff)):
            product.append(sumpf.modules.FourierTransform(ip_filter_kernels[i]).GetSpectrum()*coeff[i])
        filter_kernel = sum(product)
        op_filter_kernels_s.append(filter_kernel)
    op_filters = []
    for spec,cons in zip(op_filter_kernels_s,constant_specs):
        op = sumpf.modules.Add(value1=spec, value2=cons).GetResult()
        op_filters.append(sumpf.modules.InverseFourierTransform(op).GetSignal())
    return op_filters

