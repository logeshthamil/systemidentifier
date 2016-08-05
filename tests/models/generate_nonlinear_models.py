import sumpf
import nlsp

def test_checkconnectors():
    ip_signal = sumpf.modules.SweepGenerator(samplingrate=48000,length=2**14).GetSignal()
    nl_system = nlsp.HammersteinGroupModel(input_signal=ip_signal,
                                           nonlinear_functions=nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_functions.Power,branches=3),
                                           filter_impulseresponses=nlsp.helper_functions.create_arrayof_bpfilter(sampling_rate=48000,branches=3),
                                           aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=1))
    nlsp.common.plot.plot(nl_system.GetOutput())

test_checkconnectors()