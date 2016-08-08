import sumpf
import nlsp
import nlsp.common.helper_functions_private as nlsp_private

def test_modify_model_constructors():
    branches = 3
    signal = sumpf.modules.SweepGenerator(samplingrate=48000, length=2**15).GetSignal()
    ref_nlfunctions1 = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_function.Power,branches)
    ref_nlfunctions2 = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_function.Power,branches)
    ref_bpfilters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000)
    ref_aliasingcomp1 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=1)
    ref_aliasingcomp2 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=1)
    ref_HGM = nlsp.HammersteinGroupModel(nonlinear_functions=ref_nlfunctions1, filter_impulseresponses=ref_bpfilters,
                                         aliasing_compensation=ref_aliasingcomp1)
    test_HGM = nlsp.HammersteinGroupModel()
    ref_HGM.SetInput(signal)
    test_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) !=\
           nlsp_private.calculateenergy_timedomain(test_HGM.GetOutput())
    modify_model = nlsp.ModifyModel(input_model=test_HGM, filter_impulseresponses=ref_bpfilters,
                                    nonlinear_functions=ref_nlfunctions2, aliasing_compensation=ref_aliasingcomp2)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) ==\
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())


def test_modify_model_SetAliasingCompensation():
    branches = 3
    signal = sumpf.modules.SweepGenerator(samplingrate=48000, length=2**15).GetSignal()
    ref_nlfunctions1 = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_function.Power,branches)
    ref_nlfunctions2 = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_function.Power,branches)
    ref_bpfilters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000)
    ref_aliasingcomp1 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=1)
    ref_aliasingcomp2 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=1)
    ref_HGM = nlsp.HammersteinGroupModel(nonlinear_functions=ref_nlfunctions1, filter_impulseresponses=ref_bpfilters,
                                         aliasing_compensation=ref_aliasingcomp1)
    test_HGM = nlsp.HammersteinGroupModel()
    ref_HGM.SetInput(signal)
    test_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) !=\
           nlsp_private.calculateenergy_timedomain(test_HGM.GetOutput())
    modify_model = nlsp.ModifyModel(input_model=test_HGM, filter_impulseresponses=ref_bpfilters,
                                    nonlinear_functions=ref_nlfunctions2)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) !=\
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())
    modify_model.SetAliasingCompensation(ref_aliasingcomp2)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) ==\
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())

def test_modify_model_SetNonlinearFunctions():
    branches = 3
    signal = sumpf.modules.SweepGenerator(samplingrate=48000, length=2**15).GetSignal()
    ref_nlfunctions1 = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_function.Power,branches)
    ref_nlfunctions2 = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_function.Power,branches)
    ref_nlfunctions3 = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_function.Power,branches)
    ref_bpfilters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000)
    ref_aliasingcomp1 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=1)
    ref_aliasingcomp2 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=1)
    ref_HGM = nlsp.HammersteinGroupModel(nonlinear_functions=ref_nlfunctions1, filter_impulseresponses=ref_bpfilters,
                                         aliasing_compensation=ref_aliasingcomp1)
    test_HGM = nlsp.HammersteinGroupModel()
    ref_HGM.SetInput(signal)
    test_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) !=\
           nlsp_private.calculateenergy_timedomain(test_HGM.GetOutput())
    modify_model = nlsp.ModifyModel(input_model=test_HGM, filter_impulseresponses=ref_bpfilters,
                                    aliasing_compensation=ref_aliasingcomp2, nonlinear_functions=reversed(ref_nlfunctions2))
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) !=\
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())
    modify_model.SetNonlinearFunctions(ref_nlfunctions3)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) ==\
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())


def test_modify_model_SetFilterImpulseResponses():
    branches = 3
    signal = sumpf.modules.SweepGenerator(samplingrate=48000, length=2**15).GetSignal()
    ref_nlfunctions1 = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_function.Power,branches)
    ref_nlfunctions2 = nlsp.helper_functions.create_arrayof_nlfunctions(nlsp.nonlinear_function.Power,branches)
    ref_bpfilters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000)
    ref_aliasingcomp1 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=1)
    ref_aliasingcomp2 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(downsampling_position=1)
    ref_HGM = nlsp.HammersteinGroupModel(nonlinear_functions=ref_nlfunctions1, filter_impulseresponses=ref_bpfilters,
                                         aliasing_compensation=ref_aliasingcomp1)
    test_HGM = nlsp.HammersteinGroupModel()
    ref_HGM.SetInput(signal)
    test_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) !=\
           nlsp_private.calculateenergy_timedomain(test_HGM.GetOutput())
    rev_bp = [i for i in reversed(ref_bpfilters)]
    modify_model = nlsp.ModifyModel(input_model=test_HGM, aliasing_compensation=ref_aliasingcomp2,
                                    nonlinear_functions=ref_nlfunctions2,
                                    filter_impulseresponses=rev_bp)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) !=\
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())
    modify_model.SetFilterImpulseResponses(filter_impulseresponses=ref_bpfilters)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) ==\
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())
