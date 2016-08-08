from .model_generator import HGMModelGenerator

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
