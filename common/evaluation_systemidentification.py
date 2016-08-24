import sumpf
import nlsp
import time
import numpy

class Evaluation_artificial(object):
    """
    The base class for the evaluation of the system identification algorithms using artificial system.
    """
    def __init__(self, reference_system=None, identification_algorithms=None, test_signal=None):
        """
        @param reference_system: the reference system object
        @param identification_algorithm: the identification algorithm object
        @param test_signal: the test signal which is used for evaluation
        """
        if reference_system is None:
            self._reference_system = nlsp.HammersteinGroupModel(nonlinear_functions=[nlsp.nonlinear_function.Power(degree=i+1) for i in range(5)],
                                                                filter_impulseresponses=nlsp.helper_functions.create_arrayof_bpfilter(),
                                                                aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
        else:
            self._reference_system = reference_system
        self._identification_algorithms = identification_algorithms
        if test_signal is None:
            self._test_signal = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.LaplaceDistribution(),seed="seed").GetSignal()
        else:
            self._test_signal = test_signal

    def SetReferenceSystem(self, reference_system=None):
        """
        Set the reference system for evaluation.
        @param reference_system: the reference system
        """
        self._reference_system = reference_system

    def SetIdentificationAlgorithms(self, identification_algorithms=None):
        """
        Set the identification algorithms.
        @param identification_algorithms: the identification algorithms
        """
        self._identification_algorithms = identification_algorithms

    def GetAccuracy(self):
        """
        This method should be overridden by the methods in the derived class.
        @return: the accuracy of the resulting model
        """
        raise NotImplementedError("This method should have been overridden in a derived class")


class AccuracyEvaluation(Evaluation_artificial):
    """
    Evaluate the accuracy of the system identification algorithm.
    """
    def __init__(self, reference_nonlinearsystem=None, identification_algorithms=None, test_signal=None):
        """
        @param reference_nonlinearsystem: the reference nonlinear system
        @param identification_algorithms: the identification algorithm
        @param test_signal: the test signal for evaluation
        """
        Evaluation_artificial.__init__(self, reference_system=reference_nonlinearsystem,
                                       identification_algorithms=identification_algorithms, test_signal=test_signal)

    def GetAccuracy(self):
        """
        Get the SER value between the output of the reference system and the output of the identified system.
        @return: the SER value
        """
        ser = []
        for identification_algorithm in self._identification_algorithms:
            excitation = identification_algorithm.GetExcitation(excitation_length=len(self._test_signal),
                                                                      excitation_sampling_rate=self._test_signal.GetSamplingRate())
            self._reference_system.SetInput(excitation)
            response = self._reference_system.GetOutput()
            identification_algorithm.SetResponse(response=response)
            model = identification_algorithm.GetOutputModel()
            model.SetInput(self._test_signal)
            self._reference_system.SetInput(self._test_signal)
            output_ref = self._reference_system.GetOutput()
            output_iden = model.GetOutput()
            evaluation = nlsp.evaluations.CompareWithReference(reference_signal=output_ref, signal_to_be_evaluated=output_iden)
            ser.append(evaluation.GetSignaltoErrorRatio()[0])
        return ser

class RobustnessEvaluationWithAddedNoise(Evaluation_artificial):
    """
    Evaluate the robustness of the system identification algorithm with added noise signal.
    """
    def __init__(self, reference_nonlinearsystem=None, identification_algorithms=None, test_signal=None,
                 noise_signal=None):
        """
        @param reference_nonlinearsystem: the reference nonlinear system
        @param identification_algorithms: the identification algorithms
        @param test_signal: the test signal for evaluation
        @param noise_signal: the noise signal which is added to the response of the reference system
        """
        Evaluation_artificial.__init__(self, reference_system=reference_nonlinearsystem,
                                       identification_algorithms=identification_algorithms, test_signal=test_signal)
        self._noise_signal = noise_signal

    def GetAccuracy(self):
        """
        Get the SER value between the output of the reference system and the output of the identified system.
        @return: the SER value
        """
        ser = []
        for identification_algorithm in self._identification_algorithms:
            excitation = identification_algorithm.GetExcitation(excitation_length=len(self._test_signal),
                                                                      excitation_sampling_rate=self._test_signal.GetSamplingRate())
            self._reference_system.SetInput(excitation)
            response = self._reference_system.GetOutput()
            self._noise_signal = nlsp.common.helper_functions_private.change_length_signal(self._noise_signal,length=len(response))
            response = response + self._noise_signal
            identification_algorithm.SetResponse(response=response)
            model = identification_algorithm.GetOutputModel()
            model.SetInput(self._test_signal)
            self._reference_system.SetInput(self._test_signal)
            output_ref = self._reference_system.GetOutput()
            output_iden = model.GetOutput()
            evaluation = nlsp.evaluations.CompareWithReference(reference_signal=output_ref, signal_to_be_evaluated=output_iden)
            ser.append(evaluation.GetSignaltoErrorRatio()[0])
        return ser

class RobustnessEvaluationWithDifferentExcitationLevel(Evaluation_artificial):
    """
    Test the robustness of the system identification algorithms with different excitation levels.
    """
    def __init__(self, reference_nonlinearsystem=None, identification_algorithms=None, test_signal=None,
                 identification_level=None, testing_level=None):
        """
        @param reference_nonlinearsystem: the reference nonlinear system
        @param identification_algorithms: the identification algorithms
        @param test_signal: the test signal for evaluation
        @param identification_level: the amplitude level of the excitation signal Eg. 1.0
        @param testing_level: the amplitude level of the test signal Eg. 1.0
        """
        Evaluation_artificial.__init__(self, reference_system=reference_nonlinearsystem,
                                       identification_algorithms=identification_algorithms, test_signal=test_signal)
        if identification_level is None:
            self._identification_level = 1.0
        else:
            self._identification_level = identification_level
        if testing_level is None:
            self._testing_level = 1.0
        else:
            self._testing_level = testing_level

    def GetAccuracy(self):
        """
        Get the SER value between the output of the reference system and the output of the identified system.
        @return: the SER value
        """
        ser = []
        for identification_algorithm in self._identification_algorithms:
            excitation = identification_algorithm.GetExcitation(excitation_length=len(self._test_signal),
                                                                      excitation_sampling_rate=self._test_signal.GetSamplingRate())
            excitation = sumpf.modules.Multiply(value1=excitation, value2=self._identification_level).GetResult()
            self._reference_system.SetInput(excitation)
            response = self._reference_system.GetOutput()
            identification_algorithm.SetResponse(response=response)
            model = identification_algorithm.GetOutputModel()
            self._test_signal = sumpf.modules.Multiply(value1=self._test_signal, value2=self._testing_level).GetResult()
            model.SetInput(self._test_signal)
            self._reference_system.SetInput(self._test_signal)
            output_ref = self._reference_system.GetOutput()
            output_iden = model.GetOutput()
            evaluation = nlsp.evaluations.CompareWithReference(reference_signal=output_ref, signal_to_be_evaluated=output_iden)
            ser.append(evaluation.GetSignaltoErrorRatio()[0])
        return ser

class PerformanceEvaluation(Evaluation_artificial):
    """
    Evaluate the performance of the system identification algorithm.
    """
    def __init__(self, identification_algorithms=None, test_signal=None, excitation_length=None, kernel_length=None):
        """
        @param reference_nonlinearsystem: the reference nonlinear system
        @param identification_algorithms: the identification algorithms
        @param test_signal: the test signal
        @param excitation_length: the excitation length
        @param kernel_length: the kernel length
        """
        reference_nonlinearsystem = sumpf.modules.ClipSignal(thresholds=(-0.8,0.8))
        Evaluation_artificial.__init__(self, reference_system=reference_nonlinearsystem,
                                       identification_algorithms=identification_algorithms, test_signal=test_signal)
        self._excitation_length = excitation_length
        if kernel_length is None:
            self._kernel_length = 2**10
        else:
            self._kernel_length = kernel_length

    def GetIdentificationComplexity(self, iterations=1):
        """
        Get the identification complexity of the system identification algorithm in seconds.
        @param iterations: the number of iterations after which the average time is taken
        @return: the identification time
        """
        i_t = []
        for identification_algorithm in self._identification_algorithms:
            iden_time = []
            for i in range(iterations):
                excitation = identification_algorithm.GetExcitation(excitation_length=len(self._test_signal),
                                                                          excitation_sampling_rate=self._test_signal.GetSamplingRate())
                self._reference_system.SetInput(excitation)
                response = self._reference_system.GetOutput()
                response = response
                iden_time_start = time.clock()
                identification_algorithm.SetResponse(response=response)
                model = identification_algorithm.GetOutputModel()
                iden_time_stop = time.clock()
                iden_time.append(iden_time_stop - iden_time_start)
            i_t.append(numpy.average(iden_time))
        return i_t

    def GetSimulationComplexity(self, iterations=1):
        """
        Get the simulation complexity of the system identification algorithm in seconds.
        @param iterations: the number of iterations after which the average time is taken
        @return: the simulation time
        """
        s_t = []
        for identification_algorithm in self._identification_algorithms:
            sim_time = []
            for i in range(iterations):
                excitation = identification_algorithm.GetExcitation(excitation_length=len(self._test_signal),
                                                                          excitation_sampling_rate=self._test_signal.GetSamplingRate())
                self._reference_system.SetInput(excitation)
                response = self._reference_system.GetOutput()
                response = response
                identification_algorithm.SetResponse(response=response)
                model = identification_algorithm.GetOutputModel()
                kernels = identification_algorithm._GetFilterImpuleResponses()
                kernels = [nlsp.common.helper_functions_private.change_length_signal(signal=kernel, length=self._kernel_length) for kernel in kernels]
                modify = nlsp.ModifyModel(input_model=model, filter_impulseresponses=kernels)
                model = modify.GetOutputModel()
                sim_time_start = time.clock()
                model.SetInput(self._test_signal)
                output_iden = model.GetOutput()
                sim_time_stop = time.clock()
                sim_time.append(sim_time_stop - sim_time_start)
            s_t.append(numpy.average(sim_time))
        return s_t