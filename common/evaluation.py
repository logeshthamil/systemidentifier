import nlsp
import sumpf

class Evaluation():
    """
    The class to evaluate the model based on the output of the nonlinear system (reference output) and the output of the
    identified nonlinear model (identified output).
    """
    def __init__(self, reference_output, identified_output):
        """
        @param reference_output: the output of the nonlinear system
        @param identified_output: the output of the identified nonlinear model
        @return:
        """
        pass

    def SetReferenceOutput(self):
        """
        Sets the output of the nonlinear system or the reference output.
        """
        pass

    def SetIdentifiedOutput(self):
        """
        Sets the output fo the identified nonlinear model or the identified output.
        """
        pass

    def GetSignaltoErrorRatio(self):
        """
        Get the Signal to Error Ratio between the reference output and the identified output.
        @return: the Signal to Error Ratio
        """
        pass

    def GetSERvsFrequency(self):
        """
        Get the spectrum of the Signal to Error Ratio.
        @return: the spectrum of the SER value
        """
        pass