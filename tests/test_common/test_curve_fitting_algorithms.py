import sumpf
import nlsp

def test_biquadtracing():
    branches = 3
    clipping_thresholds = [[-1.0,1.0],[-0.9,0.9],[-0.8,0.9]]
    filter_length = 2**8
    nonlinear_function_ref = [nlsp.nonlinear_function.HardClip(clipping_threshold=th) for th in clipping_thresholds]
    filter_impulse_responses_ref = nlsp.helper_functions.create_arrayof_complexfilters(branches=branches, filter_length=filter_length)
    ref_hgm = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_function_ref,
                                         filter_impulseresponses=filter_impulse_responses_ref,
                                         aliasing_compensation=nlsp.aliasing_compensation.NoAliasingCompensation())
    curve_tracing_filters_iir, coeff = nlsp.curve_fitting_algorithms.compute_iir_from_fir_using_curvetracing_biquads(fir_kernels=ref_hgm.GetFilterImpulseResponses(),
                                                                                                              filter_order=4, Print=False, max_iterations=10)
    assert len(curve_tracing_filters_iir) == len(coeff.coefficients) == len(coeff.frequencies)

def test_multiordertracing():
    branches = 3
    clipping_thresholds = [[-1.0,1.0],[-0.9,0.9],[-0.8,0.9]]
    filter_length = 2**8
    nonlinear_function_ref = [nlsp.nonlinear_function.HardClip(clipping_threshold=th) for th in clipping_thresholds]
    filter_impulse_responses_ref = nlsp.helper_functions.create_arrayof_complexfilters(branches=branches, filter_length=filter_length)
    ref_hgm = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_function_ref,
                                         filter_impulseresponses=filter_impulse_responses_ref,
                                         aliasing_compensation=nlsp.aliasing_compensation.NoAliasingCompensation())
    curve_tracing_filters_iir, coeff = nlsp.curve_fitting_algorithms.compute_iir_from_fir_using_curvetracing_higherorder(fir_kernels=ref_hgm.GetFilterImpulseResponses(),
                                                                                                              filter_order=4, Print=False, max_iterations=10)
    assert len(curve_tracing_filters_iir) == len(coeff.coefficients) == len(coeff.frequencies)


test_biquadtracing()
test_multiordertracing()
