from .model_generator import HGMModelGenerator
import sumpf
import nlsp

class SystemIdentification(HGMModelGenerator):
    """
    A derived class of the ModelGenerator class and an abstract base class of all the system identification algorithms.
    """
    def __init__(self, system_response=None, select_branches=None, length=2**16, sampling_rate=None):
        """
        @param system_response: the response of the nonlinear system
        @param select_branches: the branches of the model to which the filter kernels have to be found Eg. [1,2,3,4,5]
        @param length: the length of the excitation and response signals
        @param sampling_rate: the sampling rate of the excitation and response signals
        """
        if system_response is None:
            self._system_response = sumpf.Signal()
        else:
            self._system_response = system_response
        if self._select_branches is None:
            self._select_branches = [1,2,3,4,5]
        else:
            self._select_branches = select_branches
        self._length = length
        if sampling_rate is None:
            self._sampling_rate = 48000
        else:
            self._sampling_rate = sampling_rate


    def GetExcitation(self, length=None, sampling_rate=None):
        """
        This method should be overridden in the derived classes. Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @sumpf.Input(sumpf.Signal,["GetFilterImpulseResponses"])
    def SetResponse(self, response=None):
        """
        Set the response of the nonlinear system.
        @param response: the response
        """
        self._system_response = response

    def GetFilterImpuleResponses(self):
        """
        This method should be overridden in the derived classes. Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetNonlinerFunctions(self):
        """
        This method should be overridden in the derived classes. Get the nonlinear functions.
        @return: the nonlinear functions
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @sumpf.Input(tuple,["GetFilterImpulseResponses","GetNonlinearFunctions"])
    def SelectBranches(self, branches=None):
        """
        Set the branches of the model to which the filter kernels have to be found.
        @return: the branches
        """
        self._select_branches = branches

class SineSweep(SystemIdentification):
    """
    A class which identifies a model of the system using a sine sweep signal.
    """
    def GetExcitation(self, length=None, sampling_rate=None):
        """
        Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        self._length = length
        self._sampling_rate = sampling_rate
        excitation_generator = nlsp.excitation_generators.Sinesweepgenerator_Novak(sampling_rate=self._sampling_rate,
                                                                                   length=self._length)
        return excitation_generator.GetOutput()

    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        branches = max(self._select_branches)
        excitation = self.GetExcitation()
        response = self._system_response
        sweep_length = sweep_generator.GetLength()
        sweep_start_freq = sweep_generator.GetStartFrequency()
        sweep_stop_freq = sweep_generator.GetStopFrequency()
        input_sweep = sweep_generator.GetOutput()

        if isinstance(input_sweep ,(sumpf.Signal)):
            ip_signal = input_sweep
            ip_spectrum = sumpf.modules.FourierTransform(signal=input_sweep).GetSpectrum()
        else:
            ip_signal = sumpf.modules.InverseFourierTransform(spectrum=input_sweep).GetSignal()
            ip_spectrum = input_sweep
        if isinstance(output_sweep ,(sumpf.Signal)):
            op_spectrum = sumpf.modules.FourierTransform(signal=output_sweep).GetSpectrum()
        else:
            op_spectrum = output_sweep
        inversed_ip = sumpf.modules.RegularizedSpectrumInversion(spectrum=ip_spectrum,start_frequency=sweep_start_freq+50,
                                                                 stop_frequency=sweep_stop_freq-100).GetOutput()
        tf_sweep = sumpf.modules.MultiplySpectrums(spectrum1=inversed_ip, spectrum2=op_spectrum).GetOutput()
        ir_sweep = sumpf.modules.InverseFourierTransform(spectrum=tf_sweep).GetSignal()
        # nlsp.common.plots.plot(ir_sweep)
        ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(sweep_length/4)).GetOutput()
        ir_sweep_direct = nlsp.append_zeros(ir_sweep_direct)
        ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        ir_merger.AddInput(ir_sweep_direct)
        for i in range(branches-1):
            split_harm = nlsp.FindHarmonicImpulseResponse_Novak(impulse_response=ir_sweep,
                                                                harmonic_order=i+2,
                                                                sweep_generator=sweep_generator).GetHarmonicImpulseResponse()
            ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                            samplingrate=ir_sweep.GetSamplingRate(), labels=split_harm.GetLabels()))
        ir_merger = ir_merger.GetOutput()

        tf_harmonics_all = sumpf.modules.FourierTransform(signal=ir_merger).GetSpectrum()
        harmonics_tf = []
        for i in range(len(tf_harmonics_all.GetChannels())):
            tf_harmonics =  sumpf.modules.SplitSpectrum(data=tf_harmonics_all, channels=[i]).GetOutput()
            harmonics_tf.append(tf_harmonics)
        A_matrix = numpy.zeros((branches,branches),dtype=numpy.complex128)
        for n in range(0,branches):
            for m in range(0,branches):
                if ((n >=m) and ((n+m) % 2 == 0)):
                    A_matrix[m][n] = (((-1 + 0j)**(2*(n+1)-m/2))/(2**n)) * nlsp.binomial((n+1),(n-m)/2)
                else:
                    A_matrix[m][n] = 0
        A_inverse = numpy.linalg.inv(A_matrix)
        for row in range(0,len(A_inverse)):
            if row % 2 != 0.0:
                A_inverse[row] = A_inverse[row] * (0+1j)
        B = []
        for row in range(0,branches):
            A = sumpf.modules.ConstantSpectrumGenerator(value=0.0,resolution=harmonics_tf[0].GetResolution(),
                                                        length=len(harmonics_tf[0])).GetSpectrum()
            for column in range(0,branches):
                temp = sumpf.modules.AmplifySpectrum(input=harmonics_tf[column],factor=A_inverse[row][column]).GetOutput()
                A = A + temp
            B_temp = nlsp.relabel(sumpf.modules.InverseFourierTransform(A).GetSignal(),"%r harmonic identified psi" %str(row+1))
            B.append(B_temp)
        nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
        return B,nl_func


    def GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        nonlinear_functions = []
        for branch in self._select_branches:
            nonlinear_function = nlsp.nonlinear_functions.Power(degree=branch)
            nonlinear_functions.append(nonlinear_function)
        return nonlinear_functions

class CosineSweep(SystemIdentification):
    """
    A class which identifies a model of the system using a cosine sweep signal.
    """
    def GetExcitation(self, length=None, sampling_rate=None):
        """
        Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        pass

    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass

class WhiteGaussianNoiseIdentification(SystemIdentification):

    def GetExcitation(self, length=None, sampling_rate=None):
        """
        Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        pass


class MISOapproach(SystemIdentification):
    """
    A class which identifies a model of a system using a
    """
    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass

class WienerGapproach(SystemIdentification):

    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass

class Adaptive(SystemIdentification):

    def __init__(self, excitation=None, response=None, branches=5, algorithm=None, nonlinear_function=None):
        pass

    def GetExcitation(self, length=None, sampling_rate=None):
        """
        Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        pass

    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass