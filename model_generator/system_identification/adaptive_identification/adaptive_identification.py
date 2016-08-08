from nlsp.model_generator.system_identification.system_identification_approaches import SystemIdentification

class Adaptive(SystemIdentification):

    def __init__(self, excitation=None, response=None, branches=5, algorithm=None, nonlinear_function=None, length=None,
                 sampling_rate=None):
        pass

    def GetExcitation(self):
        """
        Get the excitation signal for system identification.
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