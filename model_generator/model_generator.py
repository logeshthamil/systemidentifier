import sumpf
import nlsp
import collections

class HGMModelGenerator():
    """
    An abstract base class whose instances generate models.
    """

    @sumpf.Output(nlsp.HammersteinGroupModel)
    def GetOutputModel(self):
        """
        Get the output model.
        @return: the output model
        """
        # aliasing compensation
        downsampling_position = self._aliasing_compensation._downsampling_position
        self._aliasing_compensation = self._aliasing_compensation.__class__()
        self._aliasing_compensation._SetDownsamplingPosition(downsampling_position=downsampling_position)

        # nonlinear functions
        nl_functions = []
        for nl in self._nonlinear_functions:
            degree = nl.GetMaximumHarmonics()
            nl_function = nl.__class__(degree=degree)
            nl_functions.append(nl_function)

        # model
        model = self._input_model.__class__
        self._output_model = model(nonlinear_functions=nl_functions,
                                   filter_impulseresponses=self._filter_impulseresponses,
                                   aliasing_compensation=self._aliasing_compensation)
        output_model = self._output_model
        return output_model

class ModifyModel(HGMModelGenerator):
    """
    A class to modify the parameters of a model. The parameters which can be modified are the filter impulse responses,
    the nonlinear functions and the aliasing compensation technique.
    """
    def __init__(self, input_model=None, filter_impulseresponses=None, nonlinear_functions=None,
                 aliasing_compensation=None):
        """
        @param input_model: the input model
        @param filter_impulseresponses: the filter impulse responses
        Eg. [filter_impulseresponse1, filter_impulseresponse2, ...]
        @param nonlinear_function: the nonlinear functions
        Eg. [nonlinear_function1, nonlinear_function2, ...]
        @param aliasing_compensation: the aliasing compensation technique
        Eg. nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
        """
        if input_model is None:
            self._input_model = nlsp.HammersteinGroupModel()
        else:
            self._input_model = input_model
        if filter_impulseresponses is None:
            self._filter_impulseresponses = self._input_model.GetFilterImpulseResponses()
        else:
            self._filter_impulseresponses = filter_impulseresponses
        if nonlinear_functions is None:
            self._nonlinear_functions = self._input_model.GetNonlinearFunctions()
        else:
            self._nonlinear_functions = nonlinear_functions
        if aliasing_compensation is None:
            self._aliasing_compensation = self._input_model._get_aliasing_compensation()
        else:
            self._aliasing_compensation = aliasing_compensation


    @sumpf.Input(nlsp.HammersteinGroupModel, "GetOutputModel")
    def SetInputModel(self, input_model=None):
        """
        Set the input model.
        @param input_model: the input model
        """
        self._input_model = input_model

    @sumpf.Input(tuple, "GetOutputModel")
    def SetFilterImpulseResponses(self, filter_impulseresponses=None):
        """
        Set the filter impulse responses of the model.
        @param filter_impulseresponses: the filter impulse responses
        """
        self._filter_impulseresponses = filter_impulseresponses

    @sumpf.Input(tuple, "GetOutputModel")
    def SetNonlinearFunctions(self, nonlinear_functions=None):
        """
        Set the nonlinear functions of the model.
        @param: nonlinear_functions: the nonlinear functions
        """
        self._nonlinear_functions = nonlinear_functions

    @sumpf.Input(nlsp.aliasing_compensation, "GetOutputModel")
    def SetAliasingCompensation(self, aliasing_compensation=None):
        """
        Set the aliasing compensation technique.
        @param aliasing_compensation: the aliasing compensation technique
        """
        self._aliasing_compensation = aliasing_compensation


class PredefinedModelGeneration(HGMModelGenerator):
    """
    A class to generate a model based on predefined parameters.
    """
    @staticmethod
    def distortion_box():
        """
        A factory function of the PredefinedModelGeneration class to return the parameters of a distortion box.
        @return:
        """
        return PredefinedModelGeneration(predefined_model=None)

    def __init__(self, predefined_model=None, number_of_branches=None):
        """
        @param predefined_model: the predefined model Eg. nlsp.PredefinedModelGeneration.distortion_box()
        @param number_of_branches: the total number of branches
        """
        pass

    def SelectPredefinedModel(self, predefined_model=None):
        """
        Select the predefined model class.
        @param predefined_model: the predefined model Eg. nlsp.predefinedModelGeneration.distortionbox()
        """
        pass

    def SetNumberofBranches(self):
        """
        Set the total number of branches.
        @return: the total number of branches
        """
        pass
