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


def test_saveandretreive_clippingHGM():
    """
    test save and retreive model class for HGM with clipping functions as nonlinear functions.
    """
    branches = 5
    thresholds = [[-1.0, 1.0], ] * branches
    location = "C:\Users\diplomand.8\Desktop\some1.npz"
    model = nlsp.HammersteinGroupModel(
        nonlinear_functions=[nlsp.nonlinear_function.HardClip(clipping_threshold=threshold) for threshold in
                             thresholds])
    save = nlsp.SaveHGMModel(filename=location, model=model)
    retrieve = nlsp.RetrieveHGMModel(filename=location)
    model_retrieved = retrieve.GetModel()
    sample = sumpf.modules.SweepGenerator().GetSignal()
    model.SetInput(sample)
    model_retrieved.SetInput(sample)
    evaluation = nlsp.evaluations.CompareWithReference(reference_signal=model.GetOutput(),
                                                       signal_to_be_evaluated=model_retrieved.GetOutput())
    assert evaluation.GetSignaltoErrorRatio() > 500


def test_savemodel_withclippingfunction():
    branches = 2
    artificial_location_adaptive = "O:\\Diplomanden\\Logeshwaran.Thamilselvan\\Loudspeaker nonlinearity\\models\\artificialadaptive.npz"
    method = 'Nelder-Mead'
    ref_hgm = nlsp.HammersteinGroupModel(
        nonlinear_functions=[nlsp.nonlinear_function.Power(degree=i) for i in range(branches)],
        filter_impulseresponses=nlsp.helper_functions.create_arrayof_simplefilter(branches=branches),
        aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    adaptive_identification = nlsp.system_identification.ClippingAdaptive(select_branches=range(1, branches + 1),
                                                                          excitation_length=2 ** 15,
                                                                          thresholds=[[-1.0, 1.0], [-0.9, 0.9]])
    excitation = adaptive_identification.GetExcitation()
    ref_hgm.SetInput(excitation)
    adaptive_identification.SetResponse(response=ref_hgm.GetOutput())
    output_model_adaptive = adaptive_identification.GetOutputModel()
    save_adaptive = nlsp.SaveHGMModel(filename=artificial_location_adaptive, model=output_model_adaptive)
    iden_hgm = nlsp.RetrieveHGMModel(filename=artificial_location_adaptive).GetModel()
    os.remove(artificial_location_adaptive)
