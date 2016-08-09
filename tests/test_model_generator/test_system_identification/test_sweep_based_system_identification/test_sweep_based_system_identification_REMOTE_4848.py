import nlsp

def test_identify_an_HGM_Sinesweep():
    branches = 3
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=2)
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches,sampling_rate=48000.0)
    nonlinear_functions = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_functions.Power,branches=branches)
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           aliasing_compensation=aliasing_compensation,
                                           filter_impulseresponses=linear_filters)
    identification_algorithm = nlsp.system_identification.SineSweep(select_branches=range(1,branches+1),
                                                                    aliasing_compensation=aliasing_compensation,
                                                                    excitation_length=2**16, excitation_sampling_rate=48000)
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(black_box.GetOutput())
    model_black_box = identification_algorithm.GetOutputModel()

    exc = nlsp.excitation_generators.Sinesweepgenerator_Novak(sampling_rate=48000.0, approximate_numberofsamples=2**16)
    model_black_box.SetInput(exc.GetOutput())
    black_box.SetInput(exc.GetOutput())
    evaluation = nlsp.Evaluation(reference_output=black_box.GetOutput(), identified_output=model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0] >= 100

def test_identify_an_HGM_Cosinesweep():
    branches = 3
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=2)
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches,sampling_rate=48000.0)
    nonlinear_functions = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_functions.Power,branches=branches)
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           aliasing_compensation=aliasing_compensation,
                                           filter_impulseresponses=linear_filters)
    identification_algorithm = nlsp.system_identification.CosineSweep(select_branches=range(1,branches+1),
                                                                    aliasing_compensation=aliasing_compensation,
                                                                    excitation_length=2**16, excitation_sampling_rate=48000)
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(black_box.GetOutput())
    model_black_box = identification_algorithm.GetOutputModel()

    exc = nlsp.excitation_generators.Cosinesweepgenerator_Novak(sampling_rate=48000.0, approximate_numberofsamples=2**16)
    model_black_box.SetInput(exc.GetOutput())
    black_box.SetInput(exc.GetOutput())
    evaluation = nlsp.Evaluation(reference_output=black_box.GetOutput(), identified_output=model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0] >= 100
