from .miso_approach import WhiteGaussianNoiseIdentification
import math
import sumpf
import nlsp


class WienerGapproach(WhiteGaussianNoiseIdentification):
    def _GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        excitation = self.GetExcitation()
        response = self._system_response
        variance = sumpf.modules.SignalMean(excitation * excitation).GetMean()[0]
        kernels = []
        for branch in self._select_branches:
            input = nlsp.nonlinear_function.Power(excitation, branch)
            cross_corr = sumpf.modules.CorrelateSignals(signal1=input.GetOutput(), signal2=response,
                                                        mode=sumpf.modules.CorrelateSignals.SPECTRUM).GetOutput()
            factor = 1.0 / (math.factorial(branch) * (variance ** branch))
            factor = sumpf.modules.ConstantSignalGenerator(value=factor, samplingrate=cross_corr.GetSamplingRate(),
                                                           length=len(cross_corr)).GetSignal()
            k = cross_corr * factor
            kernels.append(k)
        kernels[1] = sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=excitation.GetSamplingRate(),
                                                           length=len(cross_corr)).GetSignal()
        kernels[2] = sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=excitation.GetSamplingRate(),
                                                           length=len(cross_corr)).GetSignal()
        return kernels

    def _GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        nonlinear_functions = []
        for branch in self._select_branches:
            nonlinear_function = nlsp.nonlinear_functions.Hermite(degree=branch)
            nonlinear_functions.append(nonlinear_function)
        return nonlinear_functions
