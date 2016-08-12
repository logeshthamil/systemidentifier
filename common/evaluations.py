import math
import nlsp
import sumpf


class CompareWithReference(object):
    """
    The class to evaluate the model based on the output of the nonlinear system (reference output) and the output of the
    identified nonlinear model (identified output).
    """

    def __init__(self, reference_signal=None, signal_to_be_evaluated=None, desired_frequency_range=None):
        """
        @param reference_signal: the reference signal and it should be of datatype sumpf.Signal()
        @param signal_to_be_evaluated: the signal which has to be evaluated and it should be of datatype sumpf.Signal()
        @return:
        """
        if reference_signal is None:
            self.__reference_output = sumpf.Signal()
        else:
            self.__reference_output = reference_signal
        if signal_to_be_evaluated is None:
            self.__identified_output = signal_to_be_evaluated
        else:
            self.__identified_output = signal_to_be_evaluated
        if desired_frequency_range is None:
            self.__desired_frequency_range = [20.0, 20000.0]
        else:
            self.__desired_frequency_range = desired_frequency_range

    @sumpf.Input(sumpf.Signal, ["GetSignaltoErrorRatio", "GetSERvsFrequency"])
    def SetReferenceOutput(self, reference_output):
        """
        Sets the output of the nonlinear system or the reference output.
        """
        self.__reference_output = reference_output

    @sumpf.Input(sumpf.Signal, ["GetSignaltoErrorRatio", "GetSERvsFrequency"])
    def SetIdentifiedOutput(self, identified_output):
        """
        Sets the output fo the identified nonlinear model or the identified output.
        """
        self.__identified_output = identified_output

    @sumpf.Output(float)
    def GetSignaltoErrorRatio(self, desired_frequency_range=None):
        """
        Get the Signal to Error Ratio between the reference output and the identified output.
        @return: the Signal to Error Ratio
        """
        if desired_frequency_range is not None:
            self.__desired_frequency_range = desired_frequency_range
        ref_signalorspectrum = self.__reference_output
        iden_signalorspectrum = self.__identified_output
        try:
            if isinstance(ref_signalorspectrum, list) != True:
                observed_l = []
                observed_l.append(ref_signalorspectrum)
            else:
                observed_l = ref_signalorspectrum
            if isinstance(iden_signalorspectrum, list) != True:
                identified_l = []
                identified_l.append(iden_signalorspectrum)
            else:
                identified_l = iden_signalorspectrum
            snr = []
            for observed, identified in zip(observed_l, identified_l):
                if isinstance(observed, (sumpf.Signal, sumpf.Spectrum)) and isinstance(observed,
                                                                                       (sumpf.Signal, sumpf.Spectrum)):
                    if isinstance(observed, sumpf.Signal):
                        observed = sumpf.modules.FourierTransform(observed).GetSpectrum()
                    if isinstance(identified, sumpf.Signal):
                        identified = sumpf.modules.FourierTransform(identified).GetSpectrum()
                    if len(observed) != len(identified):
                        merged_spectrum = sumpf.modules.MergeSpectrums(spectrums=[observed, identified],
                                                                       on_length_conflict=sumpf.modules.MergeSpectrums.FILL_WITH_ZEROS).GetOutput()
                        observed = sumpf.modules.SplitSpectrum(data=merged_spectrum, channels=[0]).GetOutput()
                        identified = sumpf.modules.SplitSpectrum(data=merged_spectrum, channels=[1]).GetOutput()
                    reference = observed
                    reference = nlsp.common.helper_functions_private.cut_spectrum(reference,
                                                                                  self.__desired_frequency_range)
                    identified = nlsp.common.helper_functions_private.cut_spectrum(identified,
                                                                                   self.__desired_frequency_range)
                    noise = reference - identified
                    div = sumpf.modules.Divide(value1=identified, value2=noise).GetResult()
                    div_energy = nlsp.common.helper_functions_private.calculateenergy_betweenfreq_freqdomain(div,
                                                                                                             self.__desired_frequency_range)
                    snr.append(10 * math.log10(div_energy[0]))
                else:
                    print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"
        except ZeroDivisionError:
            snr = [float("inf"), ]
        return snr

    @sumpf.Output(sumpf.Spectrum)
    def GetSERvsFrequency(self):
        """
        Get the spectrum of the Signal to Error Ratio.
        @return: the spectrum of the SER value
        """
        ref_signalorspectrum = self.__reference_output
        iden_signalorspectrum = self.__identified_output

        if isinstance(ref_signalorspectrum, list) != True:
            observed_l = []
            observed_l.append(ref_signalorspectrum)
        else:
            observed_l = ref_signalorspectrum
        if isinstance(iden_signalorspectrum, list) != True:
            identified_l = []
            identified_l.append(iden_signalorspectrum)
        else:
            identified_l = iden_signalorspectrum
        servsfreq = None
        for observed, identified in zip(observed_l, identified_l):
            if isinstance(observed, (sumpf.Signal, sumpf.Spectrum)) and isinstance(observed,
                                                                                   (sumpf.Signal, sumpf.Spectrum)):
                if isinstance(observed, sumpf.Signal):
                    observed = sumpf.modules.FourierTransform(observed).GetSpectrum()
                if isinstance(identified, sumpf.Signal):
                    identified = sumpf.modules.FourierTransform(identified).GetSpectrum()
                if len(observed) != len(identified):
                    merged_spectrum = sumpf.modules.MergeSpectrums(spectrums=[observed, identified],
                                                                   on_length_conflict=sumpf.modules.MergeSpectrums.FILL_WITH_ZEROS).GetOutput()
                    observed = sumpf.modules.SplitSpectrum(data=merged_spectrum, channels=[0]).GetOutput()
                    identified = sumpf.modules.SplitSpectrum(data=merged_spectrum, channels=[1]).GetOutput()
                reference = observed
                reference = nlsp.common.helper_functions_private.cut_spectrum(reference, self.__desired_frequency_range)
                identified = nlsp.common.helper_functions_private.cut_spectrum(identified,
                                                                               self.__desired_frequency_range)
                noise = reference - identified
                servsfreq = identified / noise
            else:
                print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"
        return servsfreq
