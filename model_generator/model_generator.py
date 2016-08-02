
class HGMModelGenerator():
    """
    An abstract base class whose instances generate models.
    """

    def GetOutputModel(self):
        """
        Get the output model.
        @return: the output model
        """
        pass

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
        pass

    def SetInputModel(self, input_model=None):
        """
        Set the input model.
        @param input_model: the input model
        """
        pass

    def SetFilterImpulseResponses(self, filter_impulseresponses=None):
        """
        Set the filter impulse responses of the model.
        @param filter_impulseresponses: the filter impulse responses
        """
        pass

    def SetNonlinearFunctions(self, nonlinear_functions=None):
        """
        Set the nonlinear functions of the model.
        @param: nonlinear_functions: the nonlinear functions
        """
        pass

    def SetAliasingCompensation(self, aliasing_compensation=None):
        """
        Set the aliasing compensation technique.
        @param aliasing_compensation: the aliasing compensation technique
        """
        pass


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
