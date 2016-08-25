import sumpf
import nlsp

def test_MISO_NLMS_algorithm():
    """
    Test the MISO_NLMS_algorithm class by identifying a HGM.
    """
    sampling_rate = 48000
    length = 2**15
    branches = 2
    input_signal = sumpf.modules.NoiseGenerator(samplingrate=sampling_rate, length=length, seed="signal").GetSignal()
    linear_kernels = nlsp.helper_functions.create_arrayof_bpfilter(sampling_rate=sampling_rate, branches=branches)
    nl_functions_1 = [nlsp.nonlinear_function.Power(i+1) for i in range(branches)]
    nl_functions_2 = [nlsp.nonlinear_function.Power(i+1) for i in range(branches)]
    nl_system = nlsp.HammersteinGroupModel(nonlinear_functions=nl_functions_1, filter_impulseresponses=linear_kernels,
                                           aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    nl_system.SetInput(input_signal=input_signal)

    outputs = []
    nl_ = [nlsp.nonlinear_function.Power(degree=1), nlsp.nonlinear_function.Power(degree=2)]
    for nl in nl_:
        hm = nlsp.HammersteinModel(aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
                                   nonlinear_function=nl)
        hm.SetInput(input_signal)
        outputs.append(hm.GetOutput())
    outputs = sumpf.modules.MergeSignals(signals=outputs).GetOutput()
    adaptation_algorithm = nlsp.MISO_NLMS_algorithm(input_signal=outputs, filter_length=len(linear_kernels[0]),
                                                                 desired_output=nl_system.GetOutput())
    filter_kernels = adaptation_algorithm.GetFilterKernel()
    filter_kernel_1 = sumpf.modules.SplitSignal(data=filter_kernels, channels=[0]).GetOutput()
    filter_kernel_2 = sumpf.modules.SplitSignal(data=filter_kernels, channels=[1]).GetOutput()
    identified_model = nlsp.HammersteinGroupModel(nonlinear_functions=nl_functions_2, filter_impulseresponses=[filter_kernel_1, filter_kernel_2],
                                                  aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    identified_model.SetInput(input_signal=input_signal)
    evaluation = nlsp.evaluations.CompareWithReference(reference_signal=nl_system.GetOutput(), signal_to_be_evaluated=identified_model.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0][0] > 70


def test_SISO_NLMS_algorithm():
    """
    Test the SISO_NLMS_algorithm class by identifying a HGM.
    """
    sampling_rate = 48000
    length = 2**15
    branches = 2
    input_signal = sumpf.modules.NoiseGenerator(samplingrate=sampling_rate, length=length, seed="signal").GetSignal()
    linear_kernels = nlsp.helper_functions.create_arrayof_bpfilter(sampling_rate=sampling_rate, branches=branches)
    nl_functions_1 = [nlsp.nonlinear_function.Power(i+1) for i in range(branches)]
    nl_functions_2 = [nlsp.nonlinear_function.Power(i+1) for i in range(branches)]
    nl_system = nlsp.HammersteinGroupModel(nonlinear_functions=nl_functions_1, filter_impulseresponses=linear_kernels,
                                           aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    nl_system.SetInput(input_signal=input_signal)

    outputs = []
    nl_ = [nlsp.nonlinear_function.Power(degree=1), nlsp.nonlinear_function.Power(degree=2)]
    for nl in nl_:
        hm = nlsp.HammersteinModel(aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
                                   nonlinear_function=nl)
        hm.SetInput(input_signal)
        outputs.append(hm.GetOutput())
    outputs = sumpf.modules.MergeSignals(signals=outputs).GetOutput()
    adaptation_algorithm = nlsp.SISO_NLMS_algorithm(input_signal=outputs, filter_length=len(linear_kernels[0]),
                                                                 desired_output=nl_system.GetOutput())
    filter_kernels = adaptation_algorithm.GetFilterKernel()
    filter_kernel_1 = sumpf.modules.SplitSignal(data=filter_kernels, channels=[0]).GetOutput()
    filter_kernel_2 = sumpf.modules.SplitSignal(data=filter_kernels, channels=[1]).GetOutput()
    identified_model = nlsp.HammersteinGroupModel(nonlinear_functions=nl_functions_2, filter_impulseresponses=[filter_kernel_1, filter_kernel_2],
                                                  aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    identified_model.SetInput(input_signal=input_signal)
    evaluation = nlsp.evaluations.CompareWithReference(reference_signal=nl_system.GetOutput(), signal_to_be_evaluated=identified_model.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0][0] > 55