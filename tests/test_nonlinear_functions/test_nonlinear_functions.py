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
    input_signal = sumpf.modules.SweepGenerator(length=2 ** 14).GetSignal()
    nl_function1 = nlsp.nonlinear_function.Power(degree=2)
    nl_function2 = nl_function1.CreateModified()
    model1 = nlsp.HammersteinModel(nonlinear_function=nl_function1)
    model2 = nlsp.HammersteinModel(nonlinear_function=nl_function2)
    model1.SetInput(input_signal)
    model2.SetInput(input_signal)
    energy1 = nlsp.common.helper_functions_private.calculateenergy_timedomain(model1.GetOutput())
    energy2 = nlsp.common.helper_functions_private.calculateenergy_timedomain(model2.GetOutput())
    assert energy1 == energy2

def test_nonlinearfunction_degree_parameter():
    sampling_rate = 48000
    branches = 3
    input_signal = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=2**18).GetSignal()
    aliasing_compensation1 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    aliasing_compensation2 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    nonlinear_functions1 = [nlsp.nonlinear_function.Power(degree=i+1) for i in range(branches)]
    nonlinear_functions2 = [nlsp.nonlinear_function.Power(i+1) for i in range(branches)]
    # filter_spec_tofind = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=sampling_rate)
    # ref_nlsystem1 = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions1,
    #                                           filter_impulseresponses=filter_spec_tofind,
    #                                           aliasing_compensation=aliasing_compensation1)
    # ref_nlsystem2 = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions2,
    #                                           filter_impulseresponses=filter_spec_tofind,
    #                                           aliasing_compensation=aliasing_compensation2)
    # ref_nlsystem1.SetInput(input_signal)
    # ref_nlsystem2.SetInput(input_signal)
    # nlsp.plots.plot(ref_nlsystem1.GetOutput(),show=False)
    # nlsp.plots.plot(ref_nlsystem2.GetOutput())
    nonlinear_function1 = nlsp.nonlinear_function.Power(2)
    nonlinear_function2 = nlsp.nonlinear_function.Power(degree=2)
    nonlinear_function1.SetInput(input_signal)
    nonlinear_function2.SetInput(input_signal)
    nlsp.plots.plot(nonlinear_function1.GetOutput(), show=False)
    nlsp.plots.plot(nonlinear_function2.GetOutput())


test_nonlinearfunction_degree_parameter()
