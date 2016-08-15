import sumpf
import nlsp

def test_identify_an_HGM_MISO():
    branches = 3
    aliasing_compensation = nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation()
    linear_filters = nlsp.helper_functions.create_arrayof_bpfilter(branches=branches, sampling_rate=48000.0)
    nonlinear_functions = [nlsp.nonlinear_function.Power(i + 1) for i in range(branches)]
    black_box = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                           aliasing_compensation=aliasing_compensation,
                                           filter_impulseresponses=linear_filters)
    identification_algorithm = nlsp.system_identification.MISOapproach(select_branches=range(1, branches + 1), )
    excitation = identification_algorithm.GetExcitation()
    black_box.SetInput(excitation)
    identification_algorithm.SetResponse(response=black_box.GetOutput())
    filt = identification_algorithm._GetFilterImpuleResponses()[0]
    hm = nlsp.HammersteinModel(nonlinear_function=identification_algorithm._GetNonlinerFunctions()[0],
                               filter_impulseresponse=filt)
    hm.SetInput(excitation)
    nlsp.plots.plot(hm.GetOutput())
    # nlsp.plots.plot(sumpf.modules.FourierTransform(black_box.GetOutput()).GetSpectrum(),show=False)
    # nlsp.plots.plot(model_black_box.GetOutput(),show=True)
    # evaluation = nlsp.evaluations.CompareWithReference(black_box.GetOutput(), model_black_box.GetOutput())
    # assert evaluation.GetSignaltoErrorRatio()[0] >= 40
