import nlsp


def test_identify_an_HGM_Sinesweep():
    branches = 3
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, samplingrate=48000.0)
    nonlinear_functions = [nlsp.nonlinear_function.Power(degree=i + 1) for i in range(branches)]
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           filter_impulseresponses=linear_filters,
                                           aliasing_compensation=aliasing_compensation)
    identification_algorithm = nlsp.system_identification.SineSweep(select_branches=range(1, branches + 1),
                                                                    aliasing_compensation=aliasing_compensation,
                                                                    excitation_length=2 ** 16,
                                                                    excitation_sampling_rate=48000)
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(black_box.GetOutput())
    model_black_box = identification_algorithm.GetOutputModel()

    exc = nlsp.excitation_generators.Sinesweepgenerator_Novak(sampling_rate=48000.0,
                                                              approximate_numberofsamples=2 ** 16)
    model_black_box.SetInput(exc.GetOutput())
    black_box.SetInput(exc.GetOutput())
    evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0] >= 100


def test_identify_an_HGM_Cosinesweep():
    branches = 3
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, samplingrate=48000.0)
    nonlinear_functions = [nlsp.nonlinear_function.Power(degree=i + 1) for i in range(branches)]
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           filter_impulseresponses=linear_filters,
                                           aliasing_compensation=aliasing_compensation)
    identification_algorithm = nlsp.system_identification.CosineSweep(select_branches=range(1, branches + 1),
                                                                      aliasing_compensation=aliasing_compensation,
                                                                      excitation_length=2 ** 16,
                                                                      excitation_sampling_rate=48000)
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(black_box.GetOutput())
    model_black_box = identification_algorithm.GetOutputModel()

    exc = nlsp.excitation_generators.Sinesweepgenerator_Novak(sampling_rate=48000.0,
                                                              approximate_numberofsamples=2 ** 16)
    model_black_box.SetInput(exc.GetOutput())
    black_box.SetInput(exc.GetOutput())
    evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0] >= 100
