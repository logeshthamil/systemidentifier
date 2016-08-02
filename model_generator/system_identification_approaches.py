from .model_generator import HGMModelGenerator

class SystemIdentification(HGMModelGenerator):
    """
    A derived class of the ModelGenerator class and an abstract base class of all the system identification algorithms.
    """
    def __init__(self, system_response=None, select_branches=None):
        """
        @param system_response: the response of the nonlinear system
        @param select_branches: the branches of the model to which the filter kernels have to be found Eg. [1,2,3,4,5]
        """
        pass

    def GetExcitation(self, length=None, sampling_rate=None):
        """
        This method should be overridden in the derived classes. Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def SetResponse(self, response=None):
        """
        Set the response of the nonlinear system.
        @param response: the response
        """
        pass

    def GetFilterImpuleResponses(self):
        """
        This method should be overridden in the derived classes. Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetNonlinerFunctions(self):
        """
        This method should be overridden in the derived classes. Get the nonlinear functions.
        @return: the nonlinear functions
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def SelectBranches(self):
        """
        Set the branches of the model to which the filter kernels have to be found.
        @return: the branches
        """
        pass

class SineSweep(SystemIdentification):
    """
    A class which identifies a model of the system using a sine sweep signal.
    """
    def GetExcitation(self, length=None, sampling_rate=None):
        """
        Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        pass

    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass

class CosineSweep(SystemIdentification):
    """
    A class which identifies a model of the system using a cosine sweep signal.
    """
    def GetExcitation(self, length=None, sampling_rate=None):
        """
        Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        pass

    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass

class WhiteGaussianNoiseIdentification(SystemIdentification):

    def GetExcitation(self, length=None, sampling_rate=None):
        """
        Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        pass


class MISOapproach(SystemIdentification):
    """
    A class which identifies a model of a system using a
    """
    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass

class WienerGapproach(SystemIdentification):

    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass

class Adaptive(SystemIdentification):

    def __init__(self, excitation=None, response=None, branches=5, algorithm=None, nonlinear_function=None):
        pass

    def GetExcitation(self, length=None, sampling_rate=None):
        """
        Get the excitation signal for system identification.
        @param length: the length
        @param sampling_rate: the sampling rate
        @return: the excitation signal
        """
        pass

    def GetFilterImpuleResponses(self):
        """
        Get the identified filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinerFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass