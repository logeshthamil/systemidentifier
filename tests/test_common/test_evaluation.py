import nlsp
import sumpf

def test_SER_multichannel():
    """
    Test the SER calculation of multichannel signals.
    """
    sampling_rate = 48000
    length = 2**16
    branches = 3
    input_signal_1 = sumpf.modules.SweepGenerator(samplingrate=sampling_rate, length=length).GetSignal()
    input_signal_2 = sumpf.modules.NoiseGenerator(samplingrate=sampling_rate, length=length).GetSignal()
    combined_signal_1 = sumpf.modules.MergeSignals(signals=[input_signal_1, input_signal_2]).GetOutput()
    combined_signal_2 = sumpf.modules.MergeSignals(signals=[input_signal_2, input_signal_1]).GetOutput()
    HGM = nlsp.HammersteinGroupModel(nonlinear_functions=[nlsp.nonlinear_function.Power(i+1) for i in range(branches)],
                                     aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    HGM.SetInput(combined_signal_1)
    output_1 = HGM.GetOutput()
    HGM.SetInput(combined_signal_2)
    output_2 = HGM.GetOutput()
    evaluation = nlsp.evaluations.CompareWithReference(output_1,output_2)
    assert len(evaluation.GetSignaltoErrorRatio()) == 2

def test_SERvsfrequency_multichannel():
    """
    Test the SER vs frequency of multichannel signals.
    """
    sampling_rate = 48000
    length = 2**16
    branches = 3
    input_signal_1 = sumpf.modules.SweepGenerator(samplingrate=sampling_rate, length=length).GetSignal()
    input_signal_2 = sumpf.modules.NoiseGenerator(samplingrate=sampling_rate, length=length).GetSignal()
    combined_signal_1 = sumpf.modules.MergeSignals(signals=[input_signal_1, input_signal_2]).GetOutput()
    combined_signal_2 = sumpf.modules.MergeSignals(signals=[input_signal_2, input_signal_1]).GetOutput()
    HGM = nlsp.HammersteinGroupModel(nonlinear_functions=[nlsp.nonlinear_function.Power(i+1) for i in range(branches)],
                                     aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    HGM.SetInput(combined_signal_1)
    output_1 = HGM.GetOutput()
    HGM.SetInput(combined_signal_2)
    output_2 = HGM.GetOutput()
    evaluation = nlsp.evaluations.CompareWithReference(output_1,output_2)
    assert len(evaluation.GetSERvsFrequency().GetChannels()) == 2