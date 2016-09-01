import sumpf
import nlsp


def test_identify_an_HGM():
    """
    Test the accuracy of identification of an HGM by MISO approach of system identification.
    """
    branches = 3
    excitation_length = 2 ** 14
    sampling_rate = 48000
    select_branches = range(1, branches + 1)
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000.0)
    nonlinear_functions = [nlsp.nonlinear_function.Power(degree=i + 1) for i in range(branches)]
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           aliasing_compensation=aliasing_compensation,
                                           filter_impulseresponses=linear_filters)
    identification_algorithm = nlsp.system_identification.MISOapproachusingHermite(select_branches=select_branches,
                                                                                   excitation_length=excitation_length,
                                                                                   excitation_sampling_rate=sampling_rate)
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(response=black_box.GetOutput())

    model_black_box = identification_algorithm.GetOutputModel()

    exc = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
                                       samplingrate=48000, length=2 ** 16).GetSignal()
    model_black_box.SetInput(exc)
    black_box.SetInput(exc)
    evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    assert evaluation.GetSignaltoErrorRatio()[0] >= 40
