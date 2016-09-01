import os
import sumpf
import nlsp


def test_saveandretrieve_accuracy():
    branches = 5
    location = "C:\Users\diplomand.8\Desktop\some.npz"
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
    os.remove(location)


def test_methods_savemodel():
    """
    Test the methods of the SaveHGMModel class.
    """
    branches = 5
    location1 = "C:\Users\diplomand.8\Desktop\some1.npz"
    location2 = "C:\Users\diplomand.8\Desktop\some2.npz"
    ref_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches)
    ref_nl = [nlsp.nonlinear_function.Power(degree=i + 1) for i in range(branches)]
    ref_aliasing = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    model1 = nlsp.HammersteinGroupModel()
    model2 = nlsp.HammersteinGroupModel(nonlinear_functions=ref_nl, filter_impulseresponses=ref_filters,
                                        aliasing_compensation=ref_aliasing)
    save_model = nlsp.SaveHGMModel(filename=location1, model=model1)
    save_model.SetFilename(location2)
    save_model.SetModel(model=model1)
    model1_retrieved = nlsp.RetrieveHGMModel(filename=location1).GetModel()
    model2_retrieved = nlsp.RetrieveHGMModel(filename=location2).GetModel()
    sample = sumpf.modules.NoiseGenerator().GetSignal()
    model1.SetInput(sample)
    model1_retrieved.SetInput(sample)
    evaluation = nlsp.evaluations.CompareWithReference(reference_signal=model1.GetOutput(),
                                                       signal_to_be_evaluated=model1_retrieved.GetOutput())
    assert evaluation.GetSignaltoErrorRatio() > 500
    evaluation.SetReferenceOutput(model2.GetOutput())
    evaluation.SetIdentifiedOutput(model2_retrieved.GetOutput())
    assert evaluation.GetSignaltoErrorRatio() > 500
    os.remove(location1)
    os.remove(location2)


def test_methods_retrievemodel():
    """
    Test the methods of the Retrieve model class.
    """
    branches = 5
    location = "C:\Users\diplomand.8\Desktop\some1.npz"
    ref_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches)
    ref_nl = [nlsp.nonlinear_function.Power(degree=i + 1) for i in range(branches)]
    ref_aliasing = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    model = nlsp.HammersteinGroupModel(nonlinear_functions=ref_nl, filter_impulseresponses=ref_filters,
                                       aliasing_compensation=ref_aliasing)
    save_model = nlsp.SaveHGMModel(filename=location, model=model)
    retrieve_model = nlsp.RetrieveHGMModel()
    try:
        retrieve_model.GetModel()
    except Exception as e:
        assert str(e) == "Please enter the filename"
    retrieve_model.SetFilename(location)
    retrieve_model.GetModel()
