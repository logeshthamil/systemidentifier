from .model_generator import HGMModelGenerator
import numpy
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
        if select_branches is None:
            self._select_branches = [1,2,3,4,5]
        else:
            self._select_branches = select_branches
        self._length = length
        if sampling_rate is None:
            self._sampling_rate = 48000
        else:
            self._sampling_rate = sampling_rate
        self._input_model = nlsp.HammersteinGroupModel()
        self._aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
        self.GetExcitation()
        self._nonlinear_functions = self.GetNonlinerFunctions()

    def GetExcitation(self):
        """
        This method should be overridden in the derived classes. Get the excitation signal for system identification.
        @return: the excitation signal
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @sumpf.Input(sumpf.Signal)
    def SetResponse(self, response=None):
        """
        Set the response of the nonlinear system.
        @param response: the response
        """
        self._system_response = response
        self._filter_impulseresponses = self.GetFilterImpuleResponses()

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
    @sumpf.Output(sumpf.Signal)
    def GetExcitation(self):
        """
        Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        self._excitation_generator = nlsp.excitation_generators.Sinesweepgenerator_Novak(sampling_rate=self._sampling_rate,
                                                                                         approximate_numberofsamples=self._length)
        return self._excitation_generator.GetOutput()

    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        branches = max(self._select_branches)
        sweep_length = self._excitation_generator.GetLength()
        rev = self._excitation_generator.GetReversedOutput()
        rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
        out_spec = sumpf.modules.FourierTransform(self._system_response).GetSpectrum()
        out_spec = out_spec / self._system_response.GetSamplingRate()
        tf = rev_spec * out_spec
        ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()
        ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(sweep_length/4)).GetOutput()
        ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        ir_merger.AddInput(ir_sweep_direct)
        for i in range(branches-1):
            split_harm = nlsp.common.FindHarmonicImpulseResponse_NovakSweep(impulse_response=ir_sweep,
                                                                            harmonic_order=i+2,
                                                                            sweep_generator=self._excitation_generator).GetHarmonicImpulseResponse()
            split_harm = sumpf.modules.CutSignal(signal=split_harm,stop=len(self._excitation_generator.GetOutput())).GetOutput()
            ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                            samplingrate=ir_sweep.GetSamplingRate(),
                                            labels=split_harm.GetLabels()))
        ir_merger = ir_merger.GetOutput()
        tf_harmonics_all = sumpf.modules.FourierTransform(ir_merger).GetSpectrum()
        harmonics_tf = []
        for i in range(len(tf_harmonics_all.GetChannels())):
            tf_harmonics =  sumpf.modules.SplitSpectrum(data=tf_harmonics_all, channels=[i]).GetOutput()
            harmonics_tf.append(tf_harmonics)
        A_matrix = numpy.zeros((branches,branches),dtype=numpy.complex128)
        for n in range(0,branches):
            for m in range(0,branches):
                if ((n >=m) and ((n+m) % 2 == 0)):
                    A_matrix[m][n] = (((-1 + 0j)**(2*(n+1)-m/2))/(2**n)) * nlsp.math.binomial_expression((n+1),(n-m)/2)
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
                temp = sumpf.modules.Multiply(value1=harmonics_tf[column], value2=A_inverse[row][column]).GetResult()
                A = A + temp
                nlsp.common.plot.plot(A,show=False)
            nlsp.common.plot.show()
            B_temp = sumpf.modules.InverseFourierTransform(A).GetSignal()
            B.append(B_temp)
        filter_kernels = []
        for branch in self._select_branches:
            filter_kernels.append(B[branch-1])
        return filter_kernels

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
    def GetExcitation(self):
        """
        Get the excitation signal for system identification.
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

    def GetExcitation(self):
        """
        Get the excitation signal for system identification.
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

    def __init__(self, excitation=None, response=None, branches=5, algorithm=None, nonlinear_function=None, length=None,
                 sampling_rate=None):
        pass

    def GetExcitation(self):
        """
        Get the excitation signal for system identification.
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