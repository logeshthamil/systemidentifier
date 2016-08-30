import sumpf
import nlsp


class SaveandRetrieveModel(object):
    """
    Save and retrieve the model.
    """

    def __init__(self, filename=None, file_format=None):
        """
        @param filename: the filename where the model has to be save or the filename of the model which has to be retrieved
        @param file_format: the file format Eg.sumpf.modules.SignalFile.NUMPY_NPZ
        """
        self._filename = filename
        self._file_format = file_format

    @sumpf.Input(str)
    def SetFilename(self, filename=None):
        """
        Set the filename where the model has to be saved or to be retrieved.
        @param filename: the filename
        """
        self._filename = filename

    @sumpf.Input(sumpf.modules.SignalFile)
    def SetFileFormat(self, file_format=None):
        """
        Set the format in which the model have to be saved.
        @param file_format: the file format Eg.sumpf.modules.SignalFile.NUMPY_NPZ
        @return:
        """
        self._file_format = file_format


class SaveModel(SaveandRetrieveModel):
    """
    Save the model in the a file location.
    """

    def __init__(self, filename=None, file_format=None, model=None):
        """
        @param filename: the file location
        @param file_format: the file format
        @param model: the model
        """
        SaveandRetrieveModel.__init__(self, filename=filename, file_format=file_format)
        self.__model = model

    def SetModel(self, model=None):
        """
        Set model model which has to be saved in the file location.
        @param model: the model
        @return:
        """
        self.__model = model


class RetrieveModel(SaveandRetrieveModel):
    """
    Retrieve the model from a specific file location.
    """

    def __init__(self, filename=None, file_format=None):
        """
        @param filename: the filename
        @param file_format: the file format
        """
        SaveandRetrieveModel.__init__(self, filename=filename, file_format=file_format)

    def GetModel(self):
        """
        Get the model which is saved in the file location.
        """
        pass


def generate_label(nonlinearfunction_class, nonlinearfunction_degree, aliasingcomp_type, aliasingcomp_loc):
    """
    A helper function to generate a label based on model parameters.
    @param nonlinearfunction_class: the class of the nonlinear block
    @param nonlinearfunction_degree: the degree of the nonlinear function
    @param aliasingcomp_type: the type of aliasing compensation
    @param aliasingcomp_loc: the location in which the aliasing compensation is done
    @return: the label
    """
    pass


def decode_label(label):
    """
    Decodes the label to different parameters of the model.
    @param label: the label
    @return: nonlinearfunction_class, nonlinearfunction_degree, aliasingcomp_type, aliasingcomp_loc
    """
    pass
