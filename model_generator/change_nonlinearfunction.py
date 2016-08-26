from model_generator import HGMModelGenerator
import sumpf
import nlsp
from nlsp.nonlinear_functions.nonlinear_functions import PolynomialNonlinearBlock

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
            elif self.__nonlinear_function is nlsp.nonlinear_function.Chebyshev:
                print "cheby"
            elif self.__nonlinear_function is nlsp.nonlinear_function.Hermite:
                print "hermite"
            elif self.__nonlinear_function is nlsp.nonlinear_function.Legendre:
                print "legendre"
            self._filter_impulseresponses = ref_filter