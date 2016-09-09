import sumpf
import nlsp
import models.generate_nonlinearmodels

class CompareModels(object):
    """
    An abstract base class to compare two models.
    """
    def __init__(self, model_1=None, model_2=None):
        """
        :param model_1: the first model
        :type model_1: nlsp.models
        :param model_2: the second model
        :type model_2: nlsp.models
        """
        if model_1 is None:
            self._model_1 = nlsp.HammersteinGroupModel()
        else:
            self._model_1 = model_1
        if model_2 is None:
            self._model_2 = nlsp.HammersteinGroupModel()
        else:
            self._model_2 = model_2

    @sumpf.Input(models.generate_nonlinearmodels, ["GetAccuracy",])
    def SetModel1(self, model_1):
        """
        Set the first model.

        :param model_1: the first model
        :type model_1: nlsp.models
        """
        self._model_1 = model_1

    @sumpf.Input(models.generate_nonlinearmodels, ["GetAccuracy",])
    def SetModel2(self, model_2):
        """
        Set the second model.

        :param model_2: the second model
        :type model_2: nlsp.models
        """
        self._model_2 = model_2

    @sumpf.Output(tuple)
    def GetAccuracy(self):
        """
        This method should be overridden in the derived classes. Get the accuracy of the input models.

        :return: the model's accuracy
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

class CompareModelsAccuracy(CompareModels):
    """
    A class which compares the accuracy of two models for given input signal.
    """
    def __init__(self, model_ref=None, model_iden=None, input_signal=None):
        self.__inputsignal = input_signal
        CompareModels.__init__(self, model_1=model_ref, model_2=model_iden)

    @sumpf.Input(sumpf.Signal, ["GetAccuracy",])
    def SetInputSignal(self, input_signal):
        self.__inputsignal = input_signal

    @sumpf.Output(tuple, ["GetAccuracy",])
    def GetAccuracy(self):
        if self.__inputsignal is None:
            self.__inputsignal = sumpf.modules.SweepGenerator(length=2**18).GetSignal()
        self._model_1.SetInput(self.__inputsignal)
        self._model_2.SetInput(self.__inputsignal)
        ref = self._model_1.GetOutput()
        iden = self._model_2.GetOutput()
        compare = nlsp.evaluations.CompareWithReference(reference_signal=ref, signal_to_be_evaluated=iden)
        return compare.GetSignaltoErrorRatio()
