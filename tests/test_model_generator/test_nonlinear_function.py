import sumpf
import nlsp

def test_recomputefilterkernels():
    ref_nlsystem = sumpf.modules.ClipSignal(thresholds=[-0.9,0.9])
    system_iden = nlsp.system_identification.SineSweep()
    excitation = system_iden.GetExcitation()
    ref_nlsystem.SetInput(excitation)
    response = ref_nlsystem.GetOutput()
    system_iden.SetResponse(response)
    output_model = system_iden.GetOutputModel()
    recompute_filterkernels = nlsp.RecomputeFilterKernels(input_model=output_model)
    recompute_filterkernels.SetNonlinearFunction(nonlinearfunction=nlsp.nonlinear_function.Power)
    modified_output_model = recompute_filterkernels.GetOutputModel()
    sample_signal = sumpf.modules.SweepGenerator().GetSignal()
    output_model.SetInput(sample_signal)
    modified_output_model.SetInput(sample_signal)
    ref_nlsystem.SetInput(sample_signal)
    eval = nlsp.evaluations.CompareWithReference(reference_signal=output_model.GetOutput(), signal_to_be_evaluated=modified_output_model.GetOutput())
    print eval.GetSignaltoErrorRatio()
    # nlsp.plots.relabelandplot(ref_nlsystem.GetOutput(),label="reference",show=False)
    # nlsp.plots.relabelandplot(output_model.GetOutput(),label="identified",show=False)
    # nlsp.plots.relabelandplot(modified_output_model.GetOutput(),label="identified_m",show=True)

test_recomputefilterkernels()