import sumpf
import nlsp


def test_saveandretrieve_accuracy():
    branches = 10
    location = "C:\Users\diplomand.8\Desktop\save\some"
    ref_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches)
    ref_nl = [nlsp.nonlinear_function.Power(degree=i + 1) for i in range(branches)]
    ref_aliasing = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    model = nlsp.HammersteinGroupModel(nonlinear_functions=ref_nl, filter_impulseresponses=ref_filters,
                                       aliasing_compensation=ref_aliasing)
    nlsp.SaveHGMModel(filename=location, model=model)
    model_retrieved = nlsp.RetrieveHGMModel(filename=location)
    model_retrieved = model_retrieved.GetModel()
    sample = sumpf.modules.SweepGenerator().GetSignal()
    model.SetInput(sample)
    model_retrieved.SetInput(sample)
    evaluation = nlsp.evaluations.CompareWithReference(reference_signal=model.GetOutput(),
                                                       signal_to_be_evaluated=model_retrieved.GetOutput())
    assert evaluation.GetSignaltoErrorRatio() > 500
