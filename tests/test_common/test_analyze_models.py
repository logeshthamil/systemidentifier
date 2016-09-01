import numpy
import nlsp


def test_calculate_energy_of_filterkernels():
    branches = 5
    nl_system = nlsp.HammersteinModel(
        nonlinear_function=nlsp.nonlinear_function.HardClip(clipping_threshold=[-0.8, 0.8]),
        aliasing_compensation=nlsp.aliasing_compensation.ReducedUpsamplingAliasingCompensation(),
        filter_impulseresponse=nlsp.helper_functions.create_arrayof_bpfilter()[0])
    system_identification = nlsp.system_identification.CosineSweep(select_branches=range(1, branches + 1),
                                                                   excitation_length=2 ** 18)
    excitation = system_identification.GetExcitation()
    nl_system.SetInput(excitation)
    response = nl_system.GetOutput()
    system_identification.SetResponse(response)
    model = system_identification.GetOutputModel()
    analyze = nlsp.analyze_models.CalculateEnergyofFilterKernels()
    analyze.SetModel(model)
    energy = analyze.GetResult()
    diff = numpy.sum(energy) / energy[0][0] + energy[2][0] + energy[4][0]
    assert int(diff) == 1
