import sumpf
import nlsp

def test_recomputefilterkernels():
    ref_nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=[nlsp.nonlinear_function.Power(degree=i+1) for i in range(5)],
                                              aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    system_iden = nlsp.system_identification.SineSweep()
    excitation = system_iden.GetExcitation()
    ref_nlsystem.SetInput(excitation)
    response = ref_nlsystem.GetOutput()
    system_iden.SetResponse(response)
    output_model = system_iden.GetOutputModel()
    recompute_filterkernels = nlsp.RecomputeFilterKernels(input_model=output_model)
    recompute_filterkernels.SetNonlinearFunction(nonlinearfunction=nlsp.nonlinear_function.Hermite)
    modified_output_model = recompute_filterkernels.GetOutputModel()
    sample_signal = sumpf.modules.SweepGenerator().GetSignal()
    output_model.SetInput(sample_signal)
    modified_output_model.SetInput(sample_signal)
    ref_nlsystem.SetInput(sample_signal)
    eval_model = nlsp.evaluations.CompareWithReference(reference_signal=ref_nlsystem.GetOutput(), signal_to_be_evaluated=output_model.GetOutput())
    eval_modifiedmodel = nlsp.evaluations.CompareWithReference(reference_signal=ref_nlsystem.GetOutput(), signal_to_be_evaluated=modified_output_model.GetOutput())
    print eval_model.GetSignaltoErrorRatio()
    print eval_modifiedmodel.GetSignaltoErrorRatio()
    nlsp.plots.relabelandplot(ref_nlsystem.GetOutput(),label="reference",show=False)
    nlsp.plots.relabelandplot(output_model.GetOutput(),label="identified",show=False)
    nlsp.plots.relabelandplot(modified_output_model.GetOutput(),label="identified_m",show=True)

def test_filter_kernels():
    branches = 3
    ref_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches,filter_length=2**10)
    ref_nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=[nlsp.nonlinear_function.Power(degree=i+1) for i in range(branches)],
                                              aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
                                              filter_impulseresponses=ref_filters)
    ref_nlsystem1= ref_nlsystem
    recompute_filterkernels = nlsp.RecomputeFilterKernels(input_model=ref_nlsystem1)
    recompute_filterkernels.SetNonlinearFunction(nonlinearfunction=nlsp.nonlinear_function.Hermite)
    found_filter_kernels = recompute_filterkernels._filter_impulseresponses
    mod_system = nlsp.HammersteinGroupModel(nonlinear_functions=[nlsp.nonlinear_function.Hermite(degree=i+1) for i in range(branches)],
                                              aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
                                              filter_impulseresponses=found_filter_kernels)
    ip = sumpf.modules.NoiseGenerator().GetSignal()
    ref_nlsystem.SetInput(ip)
    mod_system.SetInput(ip)
    evaluation = nlsp.evaluations.CompareWithReference(reference_signal=ref_nlsystem.GetOutput(), signal_to_be_evaluated=mod_system.GetOutput())
    print evaluation.GetSignaltoErrorRatio()

test_filter_kernels()