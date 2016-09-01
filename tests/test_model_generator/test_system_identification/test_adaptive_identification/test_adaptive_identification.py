import sumpf
import nlsp


def test_identify_a_HGM_adaptive():
    """
    Test the accuracy of adaptive system identification using a HGM.
    """
    branches = 2
    excitation_length = 2 ** 15
    sampling_rate = 48000
    select_branches = range(1, branches + 1)
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=sampling_rate)
    nonlinear_functions = [nlsp.nonlinear_function.Power(i + 1) for i in range(branches)]
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           aliasing_compensation=aliasing_compensation,
                                           filter_impulseresponses=linear_filters)
    identification_algorithm = nlsp.system_identification.Adaptive(select_branches=select_branches,
                                                                   excitation_length=excitation_length,
                                                                   nonlinear_function=nlsp.nonlinear_function.Power)
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(input_signal=excitation)
    identification_algorithm.SetResponse(response=black_box.GetOutput())
    model_black_box = identification_algorithm.GetOutputModel()
    exc = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
                                       samplingrate=48000, length=2 ** 16, seed="signal")
    model_black_box.SetInput(exc.GetSignal())
    black_box.SetInput(exc.GetSignal())
    evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio() >= 70


def test_using_different_branch_numbers():
    """
    Test the adaptive system identification using different branch numbers.
    """
    branches = 5
    excitation_length = 2 ** 15
    sampling_rate = 48000
    select_branches = range(1, branches + 1, 2)
    black_box = sumpf.modules.ClipSignal(thresholds=(-0.9, 0.9))
    identification_algorithm = nlsp.system_identification.Adaptive(select_branches=select_branches,
                                                                   excitation_length=excitation_length,
                                                                   excitation_sampling_rate=sampling_rate)
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(response=black_box.GetOutput())
    model_black_box = identification_algorithm.GetOutputModel()
    exc = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
                                       samplingrate=48000, length=2 ** 16)
    assert len(identification_algorithm._GetFilterImpuleResponses()) == len(
        identification_algorithm._GetNonlinerFunctions()) == len(select_branches)
    model_black_box.SetInput(exc.GetSignal())
    black_box.SetInput(exc.GetSignal())
    evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio() >= 65


def test_identify_a_HGM_clippingadaptive():
    """
    Test the accuracy of adaptive system identification using clipper as nonlinear function.
    """
    branches = 2
    excitation_length = 2 ** 15
    sampling_rate = 48000
    select_branches = range(1, branches + 1)
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=sampling_rate)
    nonlinear_functions = [nlsp.nonlinear_function.Power(i + 1) for i in range(branches)]
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           aliasing_compensation=aliasing_compensation,
                                           filter_impulseresponses=linear_filters)
    identification_algorithm = nlsp.system_identification.ClippingAdaptive(select_branches=range(1, 2 + 1),
                                                                           excitation_length=excitation_length,
                                                                           nonlinear_function=nlsp.nonlinear_function.HardClip,
                                                                           thresholds=[[-1.0, 1.0], [-0.9, 0.8]])
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(input_signal=excitation)
    identification_algorithm.SetResponse(response=black_box.GetOutput())
    model_black_box = identification_algorithm.GetOutputModel()
    exc = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
                                       samplingrate=48000, length=2 ** 16, seed="signal")
    model_black_box.SetInput(exc.GetSignal())
    black_box.SetInput(exc.GetSignal())
    evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio() >= 75


def test_identify_a_HGM_clippingvsclippingadaptive():
    """
    Test the comparison of accuracy between adaptive and clipping adaptive system identification.
    """
    branches = 2
    excitation_length = 2 ** 14
    sampling_rate = 48000
    select_branches = range(1, branches + 1)
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=sampling_rate)
    nonlinear_functions = [nlsp.nonlinear_function.Power(i + 1) for i in range(branches)]
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           aliasing_compensation=aliasing_compensation,
                                           filter_impulseresponses=linear_filters)
    identification_algorithm_clippingadaptive = nlsp.system_identification.ClippingAdaptive(
        select_branches=select_branches,
        excitation_length=excitation_length,
        nonlinear_function=nlsp.nonlinear_function.HardClip,
        thresholds=[[-1.0, 1.0], [-0.8, 0.9]])
    identification_algorithm_adaptive = nlsp.system_identification.Adaptive(select_branches=select_branches,
                                                                            excitation_length=excitation_length,
                                                                            nonlinear_function=nlsp.nonlinear_function.Legendre)

    excitation_adaptive = identification_algorithm_adaptive.GetExcitation()
    black_box.SetInput(input_signal=excitation_adaptive)
    identification_algorithm_adaptive.SetResponse(response=black_box.GetOutput())
    model_black_box_adaptive = identification_algorithm_adaptive.GetOutputModel()

    excitation_clippingadaptive = identification_algorithm_clippingadaptive.GetExcitation()
    black_box.SetInput(input_signal=excitation_clippingadaptive)
    identification_algorithm_clippingadaptive.SetResponse(response=black_box.GetOutput())
    model_black_box_clippingadaptive = identification_algorithm_clippingadaptive.GetOutputModel()

    exc = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
                                       samplingrate=48000, length=2 ** 14, seed="signal")
    model_black_box_adaptive.SetInput(exc.GetSignal())
    model_black_box_clippingadaptive.SetInput(exc.GetSignal())
    black_box.SetInput(exc.GetSignal())

    evaluation_adaptive = nlsp.evaluations.CompareWithReference(black_box.GetOutput(),
                                                                model_black_box_adaptive.GetOutput())
    evaluation_clippingadaptive = nlsp.evaluations.CompareWithReference(black_box.GetOutput(),
                                                                        model_black_box_clippingadaptive.GetOutput())

    assert evaluation_clippingadaptive.GetSignaltoErrorRatio()[0] > evaluation_adaptive.GetSignaltoErrorRatio()[0]
