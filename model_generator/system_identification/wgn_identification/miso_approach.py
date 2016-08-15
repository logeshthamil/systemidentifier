from nlsp.model_generator.system_identification.system_identification_approaches import SystemIdentification
import numpy
import itertools
import sumpf
import nlsp


class WhiteGaussianNoiseIdentification(SystemIdentification):
    def GetExcitation(self):
        """
        Get the excitation signal for system identification.
        @return: the excitation signal
        """
        self.__excitation_generator = sumpf.modules.NoiseGenerator(
                distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(),
                samplingrate=self._sampling_rate, length=self._length, seed="seed")
        return self.__excitation_generator.GetSignal()


class MISOapproach(WhiteGaussianNoiseIdentification):
    """
    A class which identifies a model of a system using a
    """

    def __get_K_matrix(self, input_signal):
        """
        Find the k matrix for the input signal
        :param input: the input signal
        :param total_branches: the total number of branches
        :return: the k matrix
        """
        total_branches = max(self._select_branches)
        row_array = range(0, total_branches)
        column_array = range(0, total_branches)
        k_matrix = numpy.zeros((total_branches, total_branches))
        for n, m in itertools.product(row_array, column_array):
            n = n + 1
            m = m + 1
            k_matrix[0][0] = 1.000
            k = None
            if n < m:
                k = 0
                for i in range(n, m):
                    num = nlsp.nonlinear_function.Power(degree=i + m, input_signal=input_signal)
                    den = nlsp.nonlinear_function.Power(degree=2 * i, input_signal=input_signal)
                    num = num.GetOutput()
                    den = den.GetOutput()
                    num = round(sumpf.modules.SignalMean(num).GetMean()[0], 3)
                    den = round(sumpf.modules.SignalMean(den).GetMean()[0], 3)
                    k = k + (k_matrix[n - 1][i - 1] * (num / den))
                k = -round(k, 2)
            elif n > m:
                k = 0
            elif n == m:
                k = 1
            if (n + m) % 2 == 1:
                k = 0
            k_matrix[n - 1][m - 1] = round(k, 2)
        return k_matrix

    def __get_decorrelated_output(self, input_signal):
        """
        Decorrelate the output signals of the powerseries expansion.
        :param input: the input signal
        :param total_branches: the total number of branches
        :return: the decorrelated signal, the k matrix and the mu matrix
        """
        total_branches = max(self._select_branches)
        k_matrix = self.__get_K_matrix(input_signal=input_signal)
        mu_matrix = []
        signal_matrix = []
        dummy = sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=input_signal.GetSamplingRate(),
                                                      length=len(input_signal)).GetSignal()
        signal_powers = []
        for i in range(1, total_branches + 1, 1):
            power = nlsp.nonlinear_function.Power(input_signal=input_signal, degree=i)
            signal_powers.append(power.GetOutput())
        signal_powers_k = []
        k_matrix_t = numpy.transpose(k_matrix)
        for i in range(0, total_branches):
            dummy_sig = sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=input_signal.GetSamplingRate(),
                                                              length=len(input_signal)).GetSignal()
            for sig, k in zip(signal_powers, k_matrix_t[i]):
                sig = sig * k
                dummy_sig = sig + dummy_sig
            signal_powers_k.append(dummy_sig)
        for i in range(0, total_branches):
            core = signal_powers_k[i]
            if i % 2 == 0:
                power = nlsp.nonlinear_function.Power(input_signal=input_signal, degree=i)
                mu = sumpf.modules.SignalMean(signal=power.GetOutput()).GetMean()
                mu = sumpf.modules.ConstantSignalGenerator(value=float(mu[0]), samplingrate=core.GetSamplingRate(),
                                                           length=len(core)).GetSignal()
                mu_matrix.append(sumpf.modules.FourierTransform(mu).GetSpectrum())
                comb = core + mu
            else:
                mu = sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=core.GetSamplingRate(),
                                                           length=len(core)).GetSignal()
                mu_matrix.append(sumpf.modules.FourierTransform(mu).GetSpectrum())
                comb = core
            core = dummy + comb
            signal_matrix.append(core)
        return signal_matrix, k_matrix, mu_matrix

    def _GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        branches = max(self._select_branches)
        input_wgn = self.GetExcitation()
        output_wgn = self._system_response
        l = []
        L = []
        signal_matrix, k_matrix, mu_matrix = self.__get_decorrelated_output(input_signal=input_wgn)
        for branch in range(1, branches + 1):
            input_decorrelated = signal_matrix[branch - 1]
            cross_corr = sumpf.modules.CorrelateSignals(signal1=input_decorrelated, signal2=output_wgn,
                                                        mode=sumpf.modules.CorrelateSignals.SPECTRUM).GetOutput()
            num = sumpf.modules.FourierTransform(cross_corr).GetSpectrum()
            den = sumpf.modules.FourierTransform(sumpf.modules.CorrelateSignals(signal1=input_decorrelated,
                                                                                signal2=input_decorrelated,
                                                                                mode=sumpf.modules.CorrelateSignals.SPECTRUM).GetOutput()).GetSpectrum()
            linear = sumpf.modules.Divide(value1=num, value2=den).GetResult()
            kernel = sumpf.modules.InverseFourierTransform(linear).GetSignal()
            signal = sumpf.Signal(channels=kernel.GetChannels(), samplingrate=input_wgn.GetSamplingRate(),
                                  labels=kernel.GetLabels())
            l.append(signal)
            L.append(sumpf.modules.FourierTransform(signal).GetSpectrum())
        G = []
        for row in range(0, branches):
            A = sumpf.modules.ConstantSpectrumGenerator(value=0.0, resolution=L[0].GetResolution(),
                                                        length=len(L[0])).GetSpectrum()
            for column in range(0, branches):
                temp = sumpf.modules.Multiply(value1=L[column], value2=k_matrix[row][column]).GetResult()
                A = A + temp
            G.append(sumpf.modules.InverseFourierTransform(A + mu_matrix[row]).GetSignal())
        filter_kernels = []
        for branch in self._select_branches:
            filter_kernels.append(G[branch - 1])
        return filter_kernels

    def _GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        nonlinear_functions = []
        for branch in self._select_branches:
            nonlinear_func = nlsp.nonlinear_function.Power(degree=branch)
            nonlinear_functions.append(nonlinear_func)
        return nonlinear_functions
