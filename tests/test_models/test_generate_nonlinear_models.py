import sumpf
import nlsp


def test_samplingrate():
    """
    Test the HGM with different sampling rate signals.
    """
    input_signal = sumpf.modules.SweepGenerator(samplingrate=96000.0, length=2 ** 10).GetSignal()

    aliasing_compensation = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
    nonlinear_functions = nlsp.nonlinear_function.Power(degree=5)

    nl_system = nlsp.HammersteinModel(aliasing_compensation=aliasing_compensation,
                                      nonlinear_function=nonlinear_functions,
                                      downsampling_position=nlsp.HammersteinModel.AFTER_LINEAR_BLOCK,
                                      input_signal=input_signal)
    input_signal = sumpf.modules.SineWaveGenerator(samplingrate=48000, length=2 ** 11)
    nl_system.SetInput(input_signal.GetSignal())
    print nl_system.GetOutput()


def test_linearity_of_model():
    """
    Test the Hammerstein model for linearity using first order nonlinear function and all pass filter.
    """
    gen_sine = sumpf.modules.SineWaveGenerator(frequency=10000.0,
                                               phase=0.0,
                                               samplingrate=48000,
                                               length=48000).GetSignal()

    model = nlsp.HammersteinModel(input_signal=gen_sine, nonlinear_function=nlsp.nonlinear_function.Power(degree=1),
                                  aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    energy_ip = nlsp.common.helper_functions_private.calculateenergy_freqdomain(gen_sine)
    energy_op = nlsp.common.helper_functions_private.calculateenergy_freqdomain(model.GetOutput())
    assert int(energy_ip[0]) == int(energy_op[0])


def test_attenuatorofHM():
    """
    Test the full and reduced upsampling aliasing compensation technique for uniformity.
    """
    sweep = sumpf.modules.SweepGenerator(start_frequency=20.0, stop_frequency=20000.0, samplingrate=48000.0,
                                         length=2 ** 14).GetSignal()
    model1 = nlsp.HammersteinModel(input_signal=sweep, nonlinear_function=nlsp.nonlinear_function.Power(degree=2),
                                   aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
                                   downsampling_position=nlsp.HammersteinModel.AFTER_NONLINEAR_BLOCK)
    model2 = nlsp.HammersteinModel(input_signal=sweep, nonlinear_function=nlsp.nonlinear_function.Power(degree=2),
                                   aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
                                   downsampling_position=nlsp.HammersteinModel.AFTER_LINEAR_BLOCK)
    model3 = nlsp.HammersteinModel(input_signal=sweep, nonlinear_function=nlsp.nonlinear_function.Power(degree=2),
                                   aliasing_compensation=nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation(),
                                   downsampling_position=nlsp.HammersteinModel.AFTER_LINEAR_BLOCK)
    model4 = nlsp.HammersteinModel(input_signal=sweep, nonlinear_function=nlsp.nonlinear_function.Power(degree=2),
                                   aliasing_compensation=nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation(),
                                   downsampling_position=nlsp.HammersteinModel.AFTER_NONLINEAR_BLOCK)
    model1_outputenergy = nlsp.common.helper_functions_private.calculateenergy_timedomain(model1.GetOutput())[0]
    model2_outputenergy = nlsp.common.helper_functions_private.calculateenergy_timedomain(model2.GetOutput())[0]
    model3_outputenergy = nlsp.common.helper_functions_private.calculateenergy_timedomain(model3.GetOutput())[0]
    model4_outputenergy = nlsp.common.helper_functions_private.calculateenergy_timedomain(model4.GetOutput())[0]
    assert int(model1_outputenergy) == int(model4_outputenergy)
    assert int(model2_outputenergy) == int(model3_outputenergy)


def test_additioninHGM():
    """
    Construct different HM's and construct a HGM with the same parameters of the HM's. The output of the sum of HM's and
    the output of the HGM should be equal.
    """
    sweep = sumpf.modules.SweepGenerator(start_frequency=20.0, stop_frequency=20000.0, samplingrate=48000.0,
                                         length=2 ** 14).GetSignal()
    nonlinear_functions = [nlsp.nonlinear_function.Power(degree=1), nlsp.nonlinear_function.Power(degree=2),
                           nlsp.nonlinear_function.Power(degree=3)]
    nonlinear_functions1 = [nlsp.nonlinear_function.Power(degree=1), nlsp.nonlinear_function.Power(degree=2),
                            nlsp.nonlinear_function.Power(degree=3)]
    aliasing_compensation1 = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
    aliasing_compensation2 = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
    aliasing_compensation3 = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
    aliasing_compensation4 = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
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


def test_HGM():
    """
    Test the SetInput method of HammersteinGroupModel.
    """
    branches = 3
    input_signal = sumpf.modules.SweepGenerator(samplingrate=48000.0, length=2 ** 14).GetSignal()
    nonlinear_functions = [nlsp.nonlinear_functions.Power(degree=i + 1) for i in range(branches)]
    filter_irs = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000)
    HGM = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions, filter_impulseresponses=filter_irs,
                                     aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    energy1 = nlsp.common.helper_functions_private.calculateenergy_timedomain(HGM.GetOutput())
    HGM.SetInput(input_signal)
    energy2 = nlsp.common.helper_functions_private.calculateenergy_timedomain(HGM.GetOutput())
    input_signal = sumpf.modules.SineWaveGenerator(frequency=2000.0, samplingrate=48000.0, length=2 ** 14).GetSignal()
    HGM.SetInput(input_signal)
    energy3 = nlsp.common.helper_functions_private.calculateenergy_timedomain(HGM.GetOutput())
    assert energy1[0] == 0.0
    assert energy2[0] != energy3[0]


def test_inputandoutputmethods_HMandHGM():
    """
    Test the input and output methods of HM and HGM.
    """
    input_signal_sweep = sumpf.modules.SweepGenerator(samplingrate=48000.0, length=2 ** 14).GetSignal()
    nonlinear_function = nlsp.nonlinear_function.Power(degree=5)
    HM = nlsp.HammersteinModel(nonlinear_function=nonlinear_function,
                               aliasing_compensation=nlsp.aliasing_compensation.NoAliasingCompensation())
    HM.SetInput(input_signal_sweep)
    output1 = HM.GetOutput()
    energy1 = nlsp.common.helper_functions_private.calculateenergy_timedomain(output1)
    input_signal_sine = sumpf.modules.SineWaveGenerator(samplingrate=48000.0, length=2 ** 14).GetSignal()
    HM.SetInput(input_signal_sine)
    output2 = HM.GetOutput()
    energy2 = nlsp.common.helper_functions_private.calculateenergy_timedomain(output2)
    assert energy1 != energy2
    nonlinear_function = nonlinear_function.CreateModified()
    HGM = nlsp.HammersteinGroupModel(nonlinear_functions=[nonlinear_function, ],
                                     aliasing_compensation=nlsp.aliasing_compensation.NoAliasingCompensation())
    HGM.SetInput(input_signal_sweep)
    energy3 = nlsp.common.helper_functions_private.calculateenergy_timedomain(HGM.GetOutput())
    assert energy1 == energy3
    HGM.SetInput(input_signal_sine)
    energy4 = nlsp.common.helper_functions_private.calculateenergy_timedomain(HGM.GetOutput())
    assert energy2 == energy4


def test_HGM_withmultichannelinput():
    """
    Test the HGM with multichannel inputs.
    """
    sampling_rate = 48000
    length = 2 ** 16
    branches = 3
    input_signal_1 = sumpf.modules.SweepGenerator(samplingrate=sampling_rate, length=length).GetSignal()
    input_signal_2 = sumpf.modules.NoiseGenerator(samplingrate=sampling_rate, length=length).GetSignal()
    combined_signal = sumpf.modules.MergeSignals(signals=[input_signal_1, input_signal_2]).GetOutput()
    linear_kernels = nlsp.helper_functions.create_arrayof_bpfilter(branches=2, sampling_rate=sampling_rate)
    linear_kernels = sumpf.modules.MergeSignals(signals=linear_kernels).GetOutput()
    HGM = nlsp.HammersteinGroupModel(
        nonlinear_functions=[nlsp.nonlinear_function.Power(i + 1) for i in range(branches)],
        aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
        filter_impulseresponses=[linear_kernels, ] * branches)
    HGM.SetInput(combined_signal)
    combined_output = HGM.GetOutput()
    HGM.SetInput(input_signal_1)
    output_1 = HGM.GetOutput()
    HGM.SetInput(input_signal_2)
    output_2 = HGM.GetOutput()
    energy_1 = nlsp.common.helper_functions_private.calculateenergy_timedomain(output_1)
    energy_2 = nlsp.common.helper_functions_private.calculateenergy_timedomain(output_2)
    combined_energy = nlsp.common.helper_functions_private.calculateenergy_timedomain(combined_output)
    assert energy_1[0] == combined_energy[0]
    assert energy_2[1] == combined_energy[1]


def test_filterlength_signallength():
    """
    Test whether the HM when the signal length is less than or equal to the filter length.
    """
    length = 2 ** 16
    sampling_rate = 48000
    sample_signal = sumpf.modules.NoiseGenerator(samplingrate=sampling_rate, length=length, seed="signal").GetSignal()
    filter_kernel = nlsp.helper_functions.create_arrayof_bpfilter(branches=1, filter_length=length)[0]
    nl_function = nlsp.nonlinear_function.Power(degree=1)
    HM = nlsp.HammersteinModel(input_signal=sample_signal, nonlinear_function=nl_function,
                               filter_impulseresponse=filter_kernel,
                               aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    ser = nlsp.evaluations.CompareWithReference(reference_signal=sample_signal, signal_to_be_evaluated=HM.GetOutput())
    assert ser.GetSignaltoErrorRatio()[0] >= 55
