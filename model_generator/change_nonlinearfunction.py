from model_generator import HGMModelGenerator
import sumpf
import nlsp
from nlsp.nonlinear_functions.nonlinear_functions import PolynomialNonlinearBlock
import numpy
from .recompute_filterkernels import anytopower, powertoany

class RecomputeFilterKernels(HGMModelGenerator):
    """
    A class to recompute the filter kernels based on the nonlinear function of the HGM.
    """

    def __init__(self, input_model=None, nonlinear_function=None):
        HGMModelGenerator.__init__(self, input_model=input_model)
        if nonlinear_function is None:
            self.__desired_nonlinear_function = nlsp.nonlinear_function.Power
        else:
            self.__desired_nonlinear_function = nonlinear_function
        self._FindFilterKernels()

    @sumpf.Input(PolynomialNonlinearBlock, "GetOutputModel")
    def SetNonlinearFunction(self, nonlinearfunction):
        """
        Set the nonlinear function of the HGM.
        @param nonlinearfunction: the nonlinear function Eg, nlsp.nonlinear_function.Power
        """
        self.__desired_nonlinear_function = nonlinearfunction
        self._FindFilterKernels()

    def _FindFilterKernels(self):
        """
        Recompute the filter kernels.
        """
        # get the parameters of the model
        modify_model = nlsp.ModifyModel(input_model=self._input_model)
        reference_nlfunctions = modify_model._nonlinear_functions
        reference_nlclass = reference_nlfunctions[0].__class__
        reference_filterkernels = modify_model._filter_impulseresponses
        reference_degreeofnl = []
        self._nonlinear_functions = []
        for nl in reference_nlfunctions:
            reference_degreeofnl.append(nl.GetMaximumHarmonics())

        # if the desired nonlinear function is same as the reference
        if self.__desired_nonlinear_function is reference_nlclass:
            self._nonlinear_functions = reference_nlfunctions
            self._filter_impulseresponses = reference_filterkernels

        # else, the desired nonlinear function is different than the reference
        else:
            for i in reference_degreeofnl:
                self._nonlinear_functions.append(self.__desired_nonlinear_function(degree=i))

            # if the desired nonlinear function is powerseries expansion
            if self.__desired_nonlinear_function is nlsp.nonlinear_function.Power:
                polynomial, coefficient = return_polynomial_and_coefficient(nl_func=reference_nlclass)
                self._filter_impulseresponses = anytopower(degree=reference_degreeofnl,
                                                           ip_filter_kernels=reference_filterkernels,
                                                           polynomial=polynomial, coefficient=coefficient)

            # else, the desired nonlinear function is other than powerseries expansion
            else:
                # if the reference nonlinear function is powerseries expansion
                if reference_nlclass is nlsp.nonlinear_function.Power:
                    polynomial, coefficient = return_polynomial_and_coefficient(
                        nl_func=self.__desired_nonlinear_function)
                    self._filter_impulseresponses = powertoany(degree=reference_degreeofnl,
                                                               ip_filter_kernels=reference_filterkernels,
                                                               polynomial=polynomial, coefficient=coefficient)
                # else, the reference nonlinear function is not a powerseries expansion
                else:
                    polynomial, coefficient = return_polynomial_and_coefficient(nl_func=reference_nlclass)
                    temp = anytopower(degree=reference_degreeofnl, ip_filter_kernels=reference_filterkernels,
                                      polynomial=polynomial, coefficient=coefficient)
                    polynomial, coefficient = return_polynomial_and_coefficient(
                        nl_func=self.__desired_nonlinear_function)
                    self._filter_impulseresponses = powertoany(degree=reference_degreeofnl, ip_filter_kernels=temp,
                                                               polynomial=polynomial, coefficient=coefficient)


def return_polynomial_and_coefficient(nl_func):
    if nl_func is nlsp.nonlinear_function.Chebyshev:
        polynomial = numpy.polynomial.chebyshev.Chebyshev
        coefficient = numpy.polynomial.chebyshev.cheb2poly
    elif nl_func is nlsp.nonlinear_function.Hermite:
        polynomial = numpy.polynomial.hermite_e.HermiteE
        coefficient = numpy.polynomial.hermite_e.herme2poly
    elif nl_func is nlsp.nonlinear_function.Legendre:
        polynomial = numpy.polynomial.legendre.Legendre
        coefficient = numpy.polynomial.legendre.leg2poly
    elif nl_func is nlsp.nonlinear_function.Laguerre:
        polynomial = numpy.polynomial.laguerre.Laguerre
        coefficient = numpy.polynomial.laguerre.lag2poly
    return polynomial, coefficient
