import sumpf
import nlsp


def test_identify_an_HGM_MISO():
    branches = 5
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, samplingrate=48000.0)
    nonlinear_functions = [nlsp.nonlinear_function.Power(i + 1) for i in range(branches)]
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           aliasing_compensation=aliasing_compensation,
                                           filter_impulseresponses=linear_filters)
    identification_algorithm = nlsp.system_identification.MISOapproach(select_branches=range(1, branches + 1), )
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(response=black_box.GetOutput())

    model_black_box = identification_algorithm.GetOutputModel()

    exc = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(),
                                       samplingrate=48000, length=2 ** 16)
    model_black_box.SetInput(exc.GetSignal())
    black_box.SetInput(exc.GetSignal())
    evaluation = nlsp.Evaluation(reference_output=black_box.GetOutput(), identified_output=model_black_box.GetOutput())
    print evaluation.GetSignaltoErrorRatio()
    assert evaluation.GetSignaltoErrorRatio()[0] >= 40
