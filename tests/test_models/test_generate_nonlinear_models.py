import sumpf
import nlsp

def test_mergerproblem():
    """
    Test the merger problem with set input signal with different sampling rate.
    """
    # TODO: at which point is merging happening in this test?
    #    can it be the case, that you test for an internal implementation detail
    #    of the HammersteinModel?
    input_signal = sumpf.modules.SweepGenerator(samplingrate=96000.0, length=2 ** 15).GetSignal()

    aliasing_compensation = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation(downsampling_position=1)
    nonlinear_functions = nlsp.nonlinear_function.Power(degree=2)

    nl_system = nlsp.HammersteinModel(aliasing_compensation=aliasing_compensation, nonlinear_function=nonlinear_functions)
    try:
        nl_system.SetInput(input_signal)
        nl_system.GetOutput()
    except Exception as e:
        # TODO: to catch all exceptions, use the base class "BaseException"
        # TODO: this is a test. It shall crash, if something goes wrong. Why do you catch this exception?
        print "Error: %s" % e

def test_linearity_of_model():
    """
    Test the Hammerstein model for linearity using first order nonlinear function and all pass filter.
    """
    gen_sine = sumpf.modules.SineWaveGenerator(frequency=10000.0,
                                      phase=0.0,
                                      samplingrate=48000,
                                      length=48000).GetSignal()

    model = nlsp.HammersteinModel(input_signal=gen_sine, nonlinear_function=nlsp.nonlinear_function.Power(degree=1),
                                  aliasing_compensation=nlsp.aliasing_compensation.LowpassAliasingCompensation())
    energy_ip = nlsp.common.helper_functions_private.calculateenergy_freqdomain(gen_sine)
    energy_op = nlsp.common.helper_functions_private.calculateenergy_freqdomain(model.GetOutput())
    assert int(energy_ip[0]) == int(energy_op[0])

def test_attenuatorofHM():
    """
    Test the attenuation factor of the Hammerstein model.
    """
    # TODO: what is the attenuation factor?
    sweep = sumpf.modules.SweepGenerator(start_frequency=20.0, stop_frequency=20000.0, samplingrate=48000.0,
                                         length=2 ** 15).GetSignal()
    model1 = nlsp.HammersteinModel(input_signal=sweep, nonlinear_function=nlsp.nonlinear_function.Power(degree=2),
                                  aliasing_compensation=nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation(downsampling_position=2))
    model2 = nlsp.HammersteinModel(input_signal=sweep, nonlinear_function=nlsp.nonlinear_function.Power(degree=2),
                                  aliasing_compensation=nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation(downsampling_position=1))
    model3 = nlsp.HammersteinModel(input_signal=sweep, nonlinear_function=nlsp.nonlinear_function.Power(degree=2),
                                  aliasing_compensation=nlsp.aliasing_compensation.LowpassAliasingCompensation())
    model1_outputenergy = nlsp.common.helper_functions_private.calculateenergy_timedomain(model1.GetOutput())[0]
    model2_outputenergy = nlsp.common.helper_functions_private.calculateenergy_timedomain(model2.GetOutput())[0]
    model3_outputenergy = nlsp.common.helper_functions_private.calculateenergy_timedomain(model3.GetOutput())[0]
    assert int(model1_outputenergy) == int(model2_outputenergy)
    assert int(model3_outputenergy) <= int(model2_outputenergy)

def test_additioninHGM():
    """
    Construct different HM's and construct a HGM with the same parameters of the HM's. The output of the sum of HM's and
    the output of the HGM should be equal.
    """
    sweep = sumpf.modules.SweepGenerator(start_frequency=20.0, stop_frequency=20000.0, samplingrate=48000.0,
                                         length=2 ** 15).GetSignal()
    nonlinear_functions = [nlsp.nonlinear_function.Power(degree=1), nlsp.nonlinear_function.Power(degree=2),
                           nlsp.nonlinear_function.Power(degree=3)]
    nonlinear_functions1 = [nlsp.nonlinear_function.Power(degree=1), nlsp.nonlinear_function.Power(degree=2),
                           nlsp.nonlinear_function.Power(degree=3)]
    aliasing_compensation1 = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation(downsampling_position=1)
    aliasing_compensation2 = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation(downsampling_position=1)
    aliasing_compensation3 = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation(downsampling_position=1)
    aliasing_compensation4 = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation(downsampling_position=1)
    model1 = nlsp.HammersteinModel(input_signal=sweep, nonlinear_function=nonlinear_functions[0],
                                   aliasing_compensation=aliasing_compensation1)
    model2 = nlsp.HammersteinModel(input_signal=sweep, nonlinear_function=nonlinear_functions[1],
                                   aliasing_compensation=aliasing_compensation2)
    model3 = nlsp.HammersteinModel(input_signal=sweep, nonlinear_function=nonlinear_functions[2],
                                  aliasing_compensation=aliasing_compensation3)
    total_output = model1.GetOutput() + model2.GetOutput() + model3.GetOutput()
    HGM = nlsp.HammersteinGroupModel(input_signal=sweep, nonlinear_functions=nonlinear_functions1,
                                     aliasing_compensation=aliasing_compensation4)
    HGM_output = HGM.GetOutput()
    assert nlsp.common.helper_functions_private.calculateenergy_timedomain(total_output) == \
           nlsp.common.helper_functions_private.calculateenergy_timedomain(HGM_output)
