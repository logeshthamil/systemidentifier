import sumpf
import nlsp
import nlsp.common.helper_functions_private as nlsp_private


def test_inputparameters_of_modifymodel():
    """
    Test the input constructors of the ModifyModel class.
    """
    branches = 3
    signal = sumpf.modules.SweepGenerator(samplingrate=48000, length=2 ** 14).GetSignal()
    ref_nlfunctions = [nlsp.nonlinear_functions.Power(degree=i + 1) for i in range(branches)]
    ref_bpfilters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000)
    ref_aliasingcomp = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    ref_HGM = nlsp.HammersteinGroupModel(nonlinear_functions=ref_nlfunctions, filter_impulseresponses=ref_bpfilters,
                                         aliasing_compensation=ref_aliasingcomp)
    test_HGM = nlsp.HammersteinGroupModel()
    ref_HGM.SetInput(signal)
    test_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) != \
           nlsp_private.calculateenergy_timedomain(test_HGM.GetOutput())
    modify_model = nlsp.ModifyModel(input_model=test_HGM, filter_impulseresponses=ref_bpfilters,
                                    nonlinear_functions=ref_nlfunctions, aliasing_compensation=ref_aliasingcomp)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) == \
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())


def test_modify_model_SetAliasingCompensation():
    """
    Test the SetAliasingCompensation method of the ModifyModel class.
    """
    branches = 3
    input_signal = sumpf.modules.SweepGenerator(samplingrate=48000.0, length=2 ** 14).GetSignal()
    nonlinear_functions = [nlsp.nonlinear_functions.Power(degree=i + 1) for i in range(branches)]
    filter_irs = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000.0)
    downsampling_posititon = nlsp.HammersteinGroupModel.AFTERNONLINEARBLOCK
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    HGM = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions, filter_impulseresponses=filter_irs,
                                     aliasing_compensation=aliasing_compensation,
                                     downsampling_position=downsampling_posititon)
    HGM.SetInput(input_signal=input_signal)
    test_HGM = nlsp.HammersteinGroupModel(downsampling_position=downsampling_posititon)
    test_HGM.SetInput(input_signal)
    energy1 = nlsp_private.calculateenergy_timedomain(HGM.GetOutput())[0]
    energy2 = nlsp_private.calculateenergy_timedomain(test_HGM.GetOutput())[0]
    assert energy1 != energy2
    modify_model = nlsp.ModifyModel(input_model=test_HGM, filter_impulseresponses=filter_irs,
                                    nonlinear_functions=nonlinear_functions,
                                    aliasing_compensation=nlsp.aliasing_compensation.NoAliasingCompensation(),
                                    downsampling_position=downsampling_posititon)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(input_signal)
    energy1 = nlsp_private.calculateenergy_timedomain(HGM.GetOutput())[0]
    energy2 = nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())[0]
    assert energy1 != energy2
    modify_model.SetAliasingCompensation(aliasing_compensation)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(input_signal)
    energy1 = nlsp_private.calculateenergy_timedomain(HGM.GetOutput())[0]
    energy2 = nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())[0]
    distance = energy1 - energy2
    distance = abs(distance)
    assert distance < 100


def test_modify_model_SetNonlinearFunctions():
    """
    Test the SetNonlinearFunctions method of the ModifyModel class.
    """
    branches = 3
    input_signal = sumpf.modules.SweepGenerator(samplingrate=48000, length=2 ** 15).GetSignal()
    ref_nlfunctions1 = [nlsp.nonlinear_functions.Power(degree=i + 1) for i in range(branches)]
    ref_nlfunctions2 = [nlsp.nonlinear_functions.Power(degree=i + 1) for i in range(branches)]
    ref_nlfunctions3 = [nlsp.nonlinear_functions.Power(degree=i + 1) for i in range(branches)]
    ref_bpfilters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000)
    ref_aliasingcomp1 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    ref_aliasingcomp2 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    ref_HGM = nlsp.HammersteinGroupModel(nonlinear_functions=ref_nlfunctions1, filter_impulseresponses=ref_bpfilters,
                                         aliasing_compensation=ref_aliasingcomp1)
    test_HGM = nlsp.HammersteinGroupModel()
    ref_HGM.SetInput(input_signal)
    test_HGM.SetInput(input_signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) != \
           nlsp_private.calculateenergy_timedomain(test_HGM.GetOutput())
    modify_model = nlsp.ModifyModel(input_model=test_HGM, filter_impulseresponses=ref_bpfilters,
                                    aliasing_compensation=ref_aliasingcomp2,
                                    nonlinear_functions=reversed(ref_nlfunctions2))
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(input_signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) != \
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())
    modify_model.SetNonlinearFunctions(ref_nlfunctions3)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(input_signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) == \
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())


def test_modify_model_SetFilterImpulseResponses():
    """
    Test the SetFilterImpulseResponses method of the ModifyModel class.
    """
    branches = 3
    downsampling_posititon = nlsp.HammersteinGroupModel.AFTERNONLINEARBLOCK
    input_signal = sumpf.modules.SweepGenerator(samplingrate=48000, length=2 ** 15).GetSignal()
    ref_nlfunctions1 = [nlsp.nonlinear_functions.Power(degree=i + 1) for i in range(branches)]
    ref_nlfunctions2 = [nlsp.nonlinear_functions.Power(degree=i + 1) for i in range(branches)]
    ref_bpfilters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000)
    ref_aliasingcomp1 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    ref_aliasingcomp2 = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    ref_HGM = nlsp.HammersteinGroupModel(nonlinear_functions=ref_nlfunctions1, filter_impulseresponses=ref_bpfilters,
                                         aliasing_compensation=ref_aliasingcomp1,
                                         downsampling_position=downsampling_posititon)
    test_HGM = nlsp.HammersteinGroupModel(downsampling_position=downsampling_posititon)
    ref_HGM.SetInput(input_signal)
    test_HGM.SetInput(input_signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) != \
           nlsp_private.calculateenergy_timedomain(test_HGM.GetOutput())
    rev_bp = [i for i in reversed(ref_bpfilters)]
    modify_model = nlsp.ModifyModel(input_model=test_HGM, aliasing_compensation=ref_aliasingcomp2,
                                    nonlinear_functions=ref_nlfunctions2,
                                    filter_impulseresponses=rev_bp)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(input_signal)
    assert nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput()) != \
           nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())
    modify_model.SetFilterImpulseResponses(filter_impulseresponses=ref_bpfilters)
    modified_HGM = modify_model.GetOutputModel()
    modified_HGM.SetInput(input_signal)
    energy1 = nlsp_private.calculateenergy_timedomain(ref_HGM.GetOutput())[0]
    energy2 = nlsp_private.calculateenergy_timedomain(modified_HGM.GetOutput())[0]
    assert int(energy1) == int(energy2)