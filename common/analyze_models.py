import sumpf
import nlsp


class AnalyzeModels(object):
    """
    A base class to analyze the model.
    """

    def __init__(self, model=None):
        """
        :param model: the instance of the nonlinear model
        """
        if model is None:
            self._input_model = nlsp.HammersteinGroupModel()
        else:
            self._input_model = model

    def SetModel(self, model):
        """
        Set the input model.

        :param model: the input model
        """
        self._input_model = model

    @sumpf.Output(tuple)
    def GetResult(self):
        """
        This method should be overridden in the derived class. Should return the result of analysis.

        :return: the result of analysis
        """
        raise NotImplementedError("This method should have been overridden in a derived class")


class CalculateEnergyofFilterKernels(AnalyzeModels):
    """
    Calculate the energy of filter kernels of the input model.
    """

    def __init__(self, model=None):
        """
        :param model: the input model
        """
        AnalyzeModels.__init__(self, model=model)

    @sumpf.Output(tuple)
    def GetResult(self):
        """
        Get the filter energy analysis report.

        :return: the energy of the filters of each branch of nonlinear model
        """
        modify = nlsp.ModifyModel(input_model=self._input_model)
        filter_kernels = modify._filter_impulseresponses
        energy = []
        for kernel in filter_kernels:
            energy.append(nlsp.common.helper_functions_private.calculateenergy_timedomain(kernel))
        return energy
