import sumpf
import nlsp


def test_inputoutput_methods():
    signal = sumpf.modules.SweepGenerator(length=2 ** 16).GetSignal()
    nl_function = nlsp.nonlinear_function.Power(degree=2, signal=signal)
    nl_function.SetInput(input_signal=signal)
    nl_function.SetDegree(degree=3)
    nl_function.GetOutput()
