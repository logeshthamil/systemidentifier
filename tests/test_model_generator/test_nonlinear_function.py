import itertools
import sumpf
import nlsp


def test_recomputefilterkernels():
    branches = 3
    ref_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, filter_length=2 ** 15)
    ref_nlsystem = nlsp.HammersteinGroupModel(
        nonlinear_functions=[nlsp.nonlinear_function.Power(degree=i + 1) for i in range(branches)],
        aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
        filter_impulseresponses=ref_filters)
    system_iden = nlsp.system_identification.SineSweep()
    excitation = system_iden.GetExcitation()
    ref_nlsystem.SetInput(excitation)
    response = ref_nlsystem.GetOutput()
    system_iden.SetResponse(response)
    output_model = system_iden.GetOutputModel()
    recompute_filterkernels = nlsp.RecomputeFilterKernels(input_model=output_model)
    recompute_filterkernels.SetNonlinearFunction(nonlinearfunction=nlsp.nonlinear_function.Laguerre)
    modified_output_model = recompute_filterkernels.GetOutputModel()
    sample_signal = sumpf.modules.NoiseGenerator().GetSignal()
    output_model.SetInput(sample_signal)
    modified_output_model.SetInput(sample_signal)
    ref_nlsystem.SetInput(sample_signal)
    evaluation = nlsp.evaluations.CompareWithReference(reference_signal=output_model.GetOutput(),
                                                       signal_to_be_evaluated=modified_output_model.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0] > 100


def filter_kernels_test():
    nl_func = [nlsp.nonlinear_function.Power, nlsp.nonlinear_function.Chebyshev, nlsp.nonlinear_function.Legendre,
               nlsp.nonlinear_function.Hermite]
    branches = 3
    ref_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, filter_length=2 ** 15)
    for nl1, nl2 in itertools.permutations(nl_func, 2):
        ref_nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=[nl1(degree=i + 1) for i in range(branches)],
                                                  aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
                                                  filter_impulseresponses=ref_filters)
        ref_nlsystem1 = ref_nlsystem
        recompute_filterkernels = nlsp.RecomputeFilterKernels(input_model=ref_nlsystem1)
        recompute_filterkernels.SetNonlinearFunction(nonlinearfunction=nl2)
        found_filter_kernels = recompute_filterkernels._filter_impulseresponses
        mod_system = nlsp.HammersteinGroupModel(nonlinear_functions=[nl2(degree=i + 1) for i in range(branches)],
                                                aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
                                                filter_impulseresponses=found_filter_kernels)
        ip = sumpf.modules.NoiseGenerator().GetSignal()
        ref_nlsystem.SetInput(ip)
        mod_system.SetInput(ip)
        evaluation = nlsp.evaluations.CompareWithReference(reference_signal=ref_nlsystem.GetOutput(),
                                                           signal_to_be_evaluated=mod_system.GetOutput())
        ser = evaluation.GetSignaltoErrorRatio()[0][0]
        print ser, nl1, nl2
