import sumpf
import nlsp
import nlsp.common.helper_functions_private as private_functions


def test_noaliasingcompensation():
    """
    Test the NoAliasingCompensation class. The NoAliasingCompensation class should not modify the signal.
    """
    input_signal = sumpf.modules.SweepGenerator(samplingrate=40000, length=2 ** 14).GetSignal()
    nl_alias = nlsp.aliasing_compensation.NoAliasingCompensation(maximum_harmonics=5)
    nl_alias.SetPreprocessingInput(input_signal)
    preprocessing_output = nl_alias.GetPreprocessingOutput()
    nl_alias.SetPostprocessingInput(input_signal)
    postprocessing_output = nl_alias.GetPostprocessingOutput()
    preprocessing_energy = private_functions.calculateenergy_timedomain(preprocessing_output)
    postprocessing_energy = private_functions.calculateenergy_timedomain(postprocessing_output)
    assert preprocessing_energy == postprocessing_energy
