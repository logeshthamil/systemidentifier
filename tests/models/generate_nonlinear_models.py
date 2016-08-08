import sumpf
import nlsp

def test_hm():
    input_signal = sumpf.modules.SweepGenerator(samplingrate=48000.0, length=2**16)

    aliasing_compensation = nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation(downsampling_position=1)
    nonlinear_functions = nlsp.nonlinear_functions.Power(degree=2)

    nl_system = nlsp.HammersteinModel(aliasing_compensation=aliasing_compensation, nonlinear_function=nonlinear_functions)
    nl_system.SetInput(input_signal.GetSignal())
    print nl_system.GetOutput()

test_hm()