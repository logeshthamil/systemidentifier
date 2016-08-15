import sumpf
import nlsp

def test_identify_an_HGM_Cosinesweep():
    """
    Test the accuracy of the Sweep based system identification using cosine sweep signal.
    """
    branches = 2
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000.0)
    nonlinear_functions = [nlsp.nonlinear_function.Power(degree=i + 1) for i in range(branches)]
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           filter_impulseresponses=linear_filters,
                                           aliasing_compensation=aliasing_compensation)
    identification_algorithm = nlsp.system_identification.CosineSweep(select_branches=range(1, branches + 1),
                                                                      aliasing_compensation=aliasing_compensation,
                                                                      excitation_length=2 ** 15,
                                                                      excitation_sampling_rate=48000)
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(black_box.GetOutput())
    model_black_box = identification_algorithm.GetOutputModel()

    exc = nlsp.excitation_generators.Sinesweepgenerator_Novak(sampling_rate=48000.0,
                                                              approximate_numberofsamples=2 ** 15)
    model_black_box.SetInput(exc.GetOutput())
    black_box.SetInput(exc.GetOutput())
    evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0] >= 100

def test_identify_an_HGM_Sinesweep():
    """
    Test the accuracy of sweep based system identification using sine sweep signal.
    """
    sampling_rate = 48000
    branches = 2
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    nonlinear_functions = [nlsp.nonlinear_function.Power(degree=i+1) for i in range(branches)]
    filter_spec_tofind = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=sampling_rate)
    ref_nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                              filter_impulseresponses=filter_spec_tofind,
                                              aliasing_compensation=aliasing_compensation)
    system_identification = nlsp.system_identification.SineSweep(select_branches=range(1,branches+1),
                                                                 aliasing_compensation=aliasing_compensation,
                                                                 excitation_length=2**16)

    excitation = system_identification.GetExcitation()
    ref_nlsystem.SetInput(excitation)
    system_identification.SetResponse(ref_nlsystem.GetOutput())
    model_black_box = system_identification.GetOutputModel()
    exc = nlsp.excitation_generators.Sinesweepgenerator_Novak(sampling_rate=48000.0,
                                                              approximate_numberofsamples=2**16)
    model_black_box.SetInput(exc.GetOutput())
    ref_nlsystem.SetInput(exc.GetOutput())
    evaluation = nlsp.evaluations.CompareWithReference(ref_nlsystem.GetOutput(), model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0] >= 100

def test_sinesweep_using_different_branch_numbers():
    """
    Test the Powerseries sweep based system identification using different branch numbers.
    """
    sampling_rate = 48000
    branches = 5
    select_branches = range(1,branches+1,2)
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    ref_nlsystem = sumpf.modules.ClipSignal(thresholds=(-0.9, 0.9))
    system_identification = nlsp.system_identification.SineSweep(select_branches=select_branches,
                                                                 aliasing_compensation=aliasing_compensation,
                                                                 excitation_length=2**14,
                                                                 excitation_sampling_rate=sampling_rate)
    excitation = system_identification.GetExcitation()
    ref_nlsystem.SetInput(excitation)
    system_identification.SetResponse(ref_nlsystem.GetOutput())
    model_black_box = system_identification.GetOutputModel()
    exc = sumpf.modules.NoiseGenerator(samplingrate=sampling_rate, length=2**14).GetSignal()
    assert len(system_identification._GetNonlinerFunctions()) == len(system_identification._GetFilterImpuleResponses()) \
           == len(select_branches)
    model_black_box.SetInput(exc)
    ref_nlsystem.SetInput(exc)
    evaluation = nlsp.evaluations.CompareWithReference(ref_nlsystem.GetOutput(), model_black_box.GetOutput())
    ser = evaluation.GetSignaltoErrorRatio()
    assert ser >= 40

def test_cosinesweep_using_different_branch_numbers():
    """
    Test the Chebyshev sweep based system identification using different branch numbers.
    """
    sampling_rate = 48000
    branches = 5
    select_branches = range(1,branches+1,2)
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    ref_nlsystem = sumpf.modules.ClipSignal(thresholds=(-0.9, 0.9))
    system_identification = nlsp.system_identification.CosineSweep(select_branches=select_branches,
                                                                 aliasing_compensation=aliasing_compensation,
                                                                 excitation_length=2**14,
                                                                 excitation_sampling_rate=sampling_rate)
    excitation = system_identification.GetExcitation()
    ref_nlsystem.SetInput(excitation)
    system_identification.SetResponse(ref_nlsystem.GetOutput())
    model_black_box = system_identification.GetOutputModel()
    exc = sumpf.modules.NoiseGenerator(samplingrate=sampling_rate, length=2**14).GetSignal()
    assert len(system_identification._GetNonlinerFunctions()) == len(system_identification._GetFilterImpuleResponses()) \
           == len(select_branches)
    model_black_box.SetInput(exc)
    ref_nlsystem.SetInput(exc)
    evaluation = nlsp.evaluations.CompareWithReference(ref_nlsystem.GetOutput(), model_black_box.GetOutput())
    ser = evaluation.GetSignaltoErrorRatio()
    assert ser >= 40
