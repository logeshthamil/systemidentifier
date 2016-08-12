import sumpf
import nlsp

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
    nlsp.plots.plot_array(identification_algorithm._GetFilterImpuleResponses(), Show=False)
    nlsp.plots.plot_array(linear_filters)
    model_black_box.SetInput(exc.GetOutput())
    black_box.SetInput(exc.GetOutput())
    nlsp.plots.plot(sumpf.modules.FourierTransform(signal=model_black_box.GetOutput()).GetSpectrum(),show=False)
    nlsp.plots.plot(sumpf.modules.FourierTransform(signal=black_box.GetOutput()).GetSpectrum(),show=True)
    evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    print evaluation.GetSignaltoErrorRatio()
    assert evaluation.GetSignaltoErrorRatio()[0] >= 100


def hgmwithfilter_evaluation():
    sampling_rate = 48000
    branches = 5
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    nonlinear_functions = [nlsp.nonlinear_function.Power(i+1) for i in range(branches)]
    filter_spec_tofind = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, samplingrate=sampling_rate)
    ref_nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                              filter_impulseresponses=filter_spec_tofind,
                                              aliasing_compensation=aliasing_compensation)
    system_identification = nlsp.system_identification.SineSweep(select_branches=range(1,branches+1),
                                                                           aliasing_compensation=aliasing_compensation,
                                                                           excitation_length=2**18)
    excitation = system_identification.GetExcitation()
    ref_nlsystem.SetInput(excitation)
    system_identification.SetResponse(ref_nlsystem.GetOutput())
    found_filter_spec = system_identification._GetFilterImpuleResponses()
    nl_functions = system_identification._GetNonlinerFunctions()
    iden_nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=nl_functions,filter_impulseresponses=found_filter_spec,
                                               aliasing_compensation=aliasing_compensation)
    iden_nlsystem.SetInput(excitation)
    nlsp.plots.plot(ref_nlsystem.GetOutput(),show=False)
    nlsp.plots.plot(iden_nlsystem.GetOutput())

def test_identify_an_HGM_Sinesweep():
    sampling_rate = 48000
    branches = 3
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    nonlinear_functions = [nlsp.nonlinear_function.Power(degree=i+1) for i in range(branches)]
    filter_spec_tofind = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=sampling_rate)
    ref_nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                              filter_impulseresponses=filter_spec_tofind,
                                              aliasing_compensation=aliasing_compensation)
    system_identification = nlsp.system_identification.SineSweep(select_branches=range(1,branches+1),
                                                                 aliasing_compensation=aliasing_compensation,
                                                                 excitation_length=2**18)

    excitation = system_identification.GetExcitation()
    ref_nlsystem.SetInput(excitation)
    system_identification.SetResponse(ref_nlsystem.GetOutput())
    model_black_box = system_identification.GetOutputModel()
    model_black_box1 = nlsp.HammersteinGroupModel(nonlinear_functions=system_identification._GetNonlinerFunctions(),
                                                  filter_impulseresponses=system_identification._GetFilterImpuleResponses(),
                                                  aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    exc = nlsp.excitation_generators.Sinesweepgenerator_Novak(sampling_rate=48000.0,
                                                              approximate_numberofsamples=2**18)
    model_black_box.SetInput(exc.GetOutput())
    model_black_box1.SetInput(exc.GetOutput())
    ref_nlsystem.SetInput(exc.GetOutput())
    nlsp.plots.plot(model_black_box.GetOutput(),show=False)
    nlsp.plots.plot(model_black_box1.GetOutput(),show=False)
    nlsp.plots.plot(ref_nlsystem.GetOutput(),show=True)
    evaluation = nlsp.evaluations.CompareWithReference(ref_nlsystem.GetOutput(), model_black_box.GetOutput())
    print evaluation.GetSignaltoErrorRatio()
    assert evaluation.GetSignaltoErrorRatio()[0] >= 100

test_identify_an_HGM_Sinesweep()