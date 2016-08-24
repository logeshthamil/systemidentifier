class AnalyzeModels(object):
    """
    A class to analyze the model.
    """

    def __init__(self, model=None):
        """
        @param model: the instance of the nonlinear model
        """
        self.__input_model = model

    def SetModel(self):
        """
        Set the instance of the nonlinear model
        """
        pass

    def GetFilterEnergyAnalysis(self):
        """
        Get the filter energy analysis report.
        @return: the energy of the filters of each branch of nonlinear model
        """
        pass
