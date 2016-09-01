import sumpf
import nlsp


def test_identify_an_HGM_WienerG():
    """
    Test the accuracy of Wiener G approach using a HGM.
    """
    branches = 2
    excitation_length = 2 ** 14
    sampling_rate = 48000
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000.0)
    nonlinear_functions = [nlsp.nonlinear_function.Power(degree=i + 1) for i in range(branches)]
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           aliasing_compensation=aliasing_compensation,
                                           filter_impulseresponses=linear_filters)
    identification_algorithm = nlsp.system_identification.WienerGapproach(select_branches=range(1, branches + 1),
                                                                          excitation_length=excitation_length,
                                                                          excitation_sampling_rate=sampling_rate)
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(response=black_box.GetOutput())

    model_black_box = identification_algorithm.GetOutputModel()

    exc = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
                                       samplingrate=48000, length=2 ** 16)
    model_black_box.SetInput(exc.GetSignal())
    black_box.SetInput(exc.GetSignal())
    evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0] >= 40


def test_identify_using_different_branches():
    """
    Test the identification of a nonlinear system using different branches of HGM.
    """
    branches = 5
    excitation_length = 2 ** 14
    sampling_rate = 48000
    select_branches = range(1, branches + 1, 2)
    black_box = sumpf.modules.ClipSignal(thresholds=(-0.9, 0.9))
    identification_algorithm = nlsp.system_identification.WienerGapproach(select_branches=select_branches,
                                                                          excitation_length=excitation_length,
                                                                          excitation_sampling_rate=sampling_rate)
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(response=black_box.GetOutput())
    model_black_box = identification_algorithm.GetOutputModel()
    assert len(identification_algorithm._GetFilterImpuleResponses()) == len(
        identification_algorithm._GetNonlinerFunctions()) \
           == len(select_branches)
    exc = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
                                       samplingrate=48000, length=2 ** 16, seed="noise")
    model_black_box.SetInput(exc.GetSignal())
    black_box.SetInput(exc.GetSignal())
    evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    ser = evaluation.GetSignaltoErrorRatio()
    assert ser >= 50


test_identify_using_different_branches()
