from .model_generator import HGMModelGenerator
import sumpf
import nlsp


class ModifyModel(HGMModelGenerator):
    """
    A class to modify the parameters of a model. The parameters which can be modified are the filter impulse responses,
    the nonlinear functions and the aliasing compensation technique.
    """

    def __init__(self, input_model=None, filter_impulseresponses=None, nonlinear_functions=None,
                 aliasing_compensation=None, downsampling_position=None):
        """
        :param input_model: the input model
        :param filter_impulseresponses: the filter impulse responses Eg, [filter_impulseresponse1, filter_impulseresponse2, ...]
        :param nonlinear_function: the nonlinear functions Eg, [nonlinear_function1, nonlinear_function2, ...]
        :param aliasing_compensation: the aliasing compensation technique Eg, nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
        :param downsampling_position: the downsampling position
        """
        HGMModelGenerator.__init__(self, input_model=input_model, filter_impulseresponses=filter_impulseresponses,
                                   nonlinear_functions=nonlinear_functions,
                                   aliasing_compensation=aliasing_compensation,
                                   downsampling_position=downsampling_position)

    @sumpf.Input(nlsp.HammersteinGroupModel, "GetOutputModel")
    def SetInputModel(self, input_model=None):
        """
        Set the input model.

        :param input_model: the input model
        """
        self._input_model = input_model

    @sumpf.Input(tuple, "GetOutputModel")
    def SetFilterImpulseResponses(self, filter_impulseresponses=None):
        """
        Set the filter impulse responses of the model.

        :param filter_impulseresponses: the filter impulse responses
        """
        self._filter_impulseresponses = filter_impulseresponses

    @sumpf.Input(tuple, "GetOutputModel")
    def SetNonlinearFunctions(self, nonlinear_functions=None):
        """
        Set the nonlinear functions of the model.

        :param: nonlinear_functions: the nonlinear functions
        """
        self._nonlinear_functions = nonlinear_functions

    @sumpf.Input(nlsp.aliasing_compensation, "GetOutputModel")
    def SetAliasingCompensation(self, aliasing_compensation=None):
        """
        Set the aliasing compensation technique.

        :param aliasing_compensation: the aliasing compensation technique
        """
        self._aliasing_compensation = aliasing_compensation
