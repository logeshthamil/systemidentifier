import sumpf
import nlsp

def test_accuracy_evaluation():
    branches = 2
    aliasing_comp = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    reference_nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=[nlsp.nonlinear_function.Power(i+1) for i in range(branches)],
                                                    filter_impulseresponses=nlsp.helper_functions.create_arrayof_bpfilter(branches=branches),
                                                    aliasing_compensation=aliasing_comp)
    identification_alg = [nlsp.system_identification.SineSweep(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.CosineSweep(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.MISOapproach(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.WienerGapproach(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.Adaptive(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp)]
    test_signal = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.LaplaceDistribution(),length=2**16).GetSignal()
    test_signal = sumpf.modules.MergeSignals(signals=[test_signal,test_signal]).GetOutput()
    evaluation = nlsp.evaluate_systemidentification.AccuracyEvaluation(reference_nonlinearsystem=reference_nlsystem,
                                                                       identification_algorithms=identification_alg,
                                                                       test_signal=test_signal)
    print evaluation.GetAccuracy()

def test_robustness_evaluation():
    branches = 2
    aliasing_comp = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    reference_nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=[nlsp.nonlinear_function.Power(i+1) for i in range(branches)],
                                                    filter_impulseresponses=nlsp.helper_functions.create_arrayof_bpfilter(branches=branches),
                                                    aliasing_compensation=aliasing_comp)
    identification_alg = [nlsp.system_identification.SineSweep(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.CosineSweep(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.MISOapproach(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.WienerGapproach(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.Adaptive(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp)]
    test_signal = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.LaplaceDistribution(),length=2**16).GetSignal()
    test_signal = sumpf.modules.MergeSignals(signals=[test_signal,test_signal]).GetOutput()
    evaluation = nlsp.evaluate_systemidentification.RobustnessEvaluationWithAddedNoise(reference_nonlinearsystem=reference_nlsystem,
                                                                       identification_algorithms=identification_alg,
                                                                       test_signal=test_signal,
                                                                       noise_signal=sumpf.modules.NoiseGenerator().GetSignal())
    print evaluation.GetAccuracy()

def test_performance_evaluation():
    branches = 2
    aliasing_comp = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    identification_alg = [nlsp.system_identification.SineSweep(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.CosineSweep(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.MISOapproach(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.WienerGapproach(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp),
                          nlsp.system_identification.Adaptive(select_branches=range(1,branches+1),aliasing_compensation=aliasing_comp)]
    test_signal = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.LaplaceDistribution(),length=2**16).GetSignal()
    test_signal = sumpf.modules.MergeSignals(signals=[test_signal,test_signal]).GetOutput()
    evaluation = nlsp.evaluate_systemidentification.PerformanceEvaluation(identification_algorithms=identification_alg,
                                                                          test_signal=test_signal)
    print evaluation.GetIdentificationComplexity()
    print evaluation.GetSimulationComplexity()