import nlsp
import sumpf


def test_SER_multichannel():
    """
    Test the SER calculation of multichannel signals.
    """
    sampling_rate = 48000
    length = 2 ** 16
    branches = 3
    input_signal_1 = sumpf.modules.SweepGenerator(samplingrate=sampling_rate, length=length).GetSignal()
    input_signal_2 = sumpf.modules.NoiseGenerator(samplingrate=sampling_rate, length=length).GetSignal()
    combined_signal_1 = sumpf.modules.MergeSignals(signals=[input_signal_1, input_signal_2]).GetOutput()
    combined_signal_2 = sumpf.modules.MergeSignals(signals=[input_signal_2, input_signal_1]).GetOutput()
    HGM = nlsp.HammersteinGroupModel(
        nonlinear_functions=[nlsp.nonlinear_function.Power(i + 1) for i in range(branches)],
        aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    HGM.SetInput(combined_signal_1)
    output_1 = HGM.GetOutput()
    HGM.SetInput(combined_signal_2)
    output_2 = HGM.GetOutput()
    evaluation = nlsp.evaluations.CompareWithReference(output_1, output_2)
    assert len(evaluation.GetSignaltoErrorRatio()[0]) == 2


def test_SERvsfrequency_multichannel():
    """
    Test the SER vs frequency of multichannel signals.
    """
    sampling_rate = 48000
    length = 2 ** 16
    branches = 3
    input_signal_1 = sumpf.modules.SweepGenerator(samplingrate=sampling_rate, length=length).GetSignal()
    input_signal_2 = sumpf.modules.NoiseGenerator(samplingrate=sampling_rate, length=length).GetSignal()
    combined_signal_1 = sumpf.modules.MergeSignals(signals=[input_signal_1, input_signal_2]).GetOutput()
    combined_signal_2 = sumpf.modules.MergeSignals(signals=[input_signal_2, input_signal_1]).GetOutput()
    HGM = nlsp.HammersteinGroupModel(
        nonlinear_functions=[nlsp.nonlinear_function.Power(i + 1) for i in range(branches)],
        aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation())
    HGM.SetInput(combined_signal_1)
    output_1 = HGM.GetOutput()
    HGM.SetInput(combined_signal_2)
    output_2 = HGM.GetOutput()
    evaluation = nlsp.evaluations.CompareWithReference(output_1, output_2)
    assert len(evaluation.GetSERvsFrequency().GetChannels()) == 2


def test_ser_inputandoutputmethods():
    ref_signal = sumpf.modules.SweepGenerator().GetSignal()
    eval_signal = 5 * ref_signal
    evaluation = nlsp.evaluations.CompareWithReference(reference_signal=ref_signal, signal_to_be_evaluated=eval_signal)
    eval_ser = evaluation.GetSignaltoErrorRatio()
    evaluation.SetIdentifiedOutput(identified_output=ref_signal)
    ref_ser = evaluation.GetSignaltoErrorRatio()
    assert eval_ser[0][0] < 100, ref_ser[0][0] > 500
