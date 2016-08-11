import sumpf
import nlsp


def test_inputandoutputmethods():
    """
    Basic test to check the input and output methods.
    """
    signal = sumpf.modules.SweepGenerator(length=2 ** 14).GetSignal()
    nl_function = nlsp.nonlinear_function.Power(degree=2, input_signal=signal)
    energy1 = nlsp.common.helper_functions_private.calculateenergy_timedomain(nl_function.GetOutput())
    nl_function.SetInput(input_signal=signal)
    nl_function.SetDegree(degree=2)
    energy2 = nlsp.common.helper_functions_private.calculateenergy_timedomain(nl_function.GetOutput())
    assert energy1 == energy2

def test_create_modified_method():
    """
    Test the Create_Modified method of the polynomial nonlinear functions class.
    """
    input_signal = sumpf.modules.SweepGenerator(length=2**14).GetSignal()
    nl_function1 = nlsp.nonlinear_function.Power(degree=2)
    nl_function2 = nl_function1.CreateModified()
    model1 = nlsp.HammersteinModel(nonlinear_function=nl_function1)
    model2 = nlsp.HammersteinModel(nonlinear_function=nl_function2)
    model1.SetInput(input_signal)
    model2.SetInput(input_signal)
    energy1 = nlsp.common.helper_functions_private.calculateenergy_timedomain(model1.GetOutput())
    energy2 = nlsp.common.helper_functions_private.calculateenergy_timedomain(model2.GetOutput())
    assert energy1 == energy2