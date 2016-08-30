from .miso_approach import WhiteGaussianNoiseIdentification
import math
import sumpf
import nlsp


class MISOapproachusingHermite(WhiteGaussianNoiseIdentification):
    """
    A class which identifies a model of a system using MISO approach which uses Hermite polynomials to decorrelate the
    input of the MISO subsystem.
    """

    def __get_decorrelated_inputs(self, input_signal, branches):
        """
        Get the array of decorrelated input signals using Hermite polynomial expansion.
        """
        decorrelated = []
        for branch in range(branches):
            nl = nlsp.nonlinear_function.Hermite(degree=branch + 1, input_signal=input_signal)
            decorrelated.append(nl.GetOutput())
        return decorrelated

    def _GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        branches = max(self._select_branches)
        input_wgn = self.GetExcitation()
        output_wgn = self._system_response
        hermite_filterkernels = []
        decorrelated_inputs = self.__get_decorrelated_inputs(input_signal=input_wgn, branches=branches)
        for branch in range(branches):
            mode = sumpf.modules.CorrelateSignals.SPECTRUM
            input_decorrelated = decorrelated_inputs[branch]
            variance = sumpf.modules.SignalMean(input_decorrelated * input_decorrelated).GetMean()[0]
            cross_corr = sumpf.modules.CorrelateSignals(signal1=input_decorrelated, signal2=output_wgn,
                                                        mode=mode).GetOutput()
            num = sumpf.modules.FourierTransform(cross_corr).GetSpectrum()
            den = sumpf.modules.FourierTransform(sumpf.modules.CorrelateSignals(signal1=input_decorrelated,
                                                                                signal2=input_decorrelated,
                                                                                mode=mode).GetOutput()).GetSpectrum()
            linear = sumpf.modules.Divide(value1=num, value2=den).GetResult()
            kernel = sumpf.modules.InverseFourierTransform(linear).GetSignal()
            signal = sumpf.Signal(channels=kernel.GetChannels(), samplingrate=input_wgn.GetSamplingRate(),
                                  labels=kernel.GetLabels())
            hermite_filterkernels.append(signal)
        return hermite_filterkernels

    def _GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        nonlinear_functions = []
        for branch in self._select_branches:
            nonlinear_func = nlsp.nonlinear_function.Hermite(degree=branch)
            nonlinear_functions.append(nonlinear_func)
        return nonlinear_functions
