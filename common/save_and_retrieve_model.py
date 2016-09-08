import numpy
import sumpf
import nlsp


class SaveandRetrieveModel(object):
    """
    Save and retrieve the model.
    """

    def __init__(self, filename=None):
        """
        :param filename: the filename where the model has to be save or the filename of the model which has to be retrieved
        """
        self._filename = filename
        self._file_format = sumpf.modules.SignalFile.NUMPY_NPZ

    @sumpf.Input(str)
    def SetFilename(self, filename=None):
        """
        Set the filename where the model has to be saved or to be retrieved.

        :param filename: the filename
        """
        self._filename = filename


class SaveHGMModel(SaveandRetrieveModel):
    """
    Save the model in the a file location.
    """

    def __init__(self, filename=None, model=None):
        """
        :param filename: the file location
        :param model: the model
        """
        SaveandRetrieveModel.__init__(self, filename=filename)
        self.__model = model
        self.__SaveModel()

    def SetModel(self, model=None):
        """
        Set model model which has to be saved in the file location.

        :param model: the model
        :type model: nlsp.models
        """
        self.__model = model
        self.__SaveModel()

    def __SaveModel(self):
        """
        Save the model in specific file location.
        """
        get_param = nlsp.ModifyModel(input_model=self.__model)
        nonlinear_functions = get_param._nonlinear_functions
        filter_kernels = get_param._filter_impulseresponses
        aliasing = get_param._aliasing_compensation
        downsampling_position = get_param._downsampling_position
        filter_kernels = sumpf.modules.MergeSignals(signals=filter_kernels).GetOutput()
        label = generate_label(nonlinearfunctions=nonlinear_functions, aliasingcomp=aliasing,
                               downsamplingposition=downsampling_position)
        model = sumpf.modules.RelabelSignal(signal=filter_kernels,
                                            labels=(label,) * len(filter_kernels.GetChannels())).GetOutput()
        sumpf.modules.SignalFile(filename=self._filename, signal=model, file_format=self._file_format).GetSignal()


class RetrieveHGMModel(SaveandRetrieveModel):
    """
    Retrieve the model from a specific file location.
    """

    def __init__(self, filename=None, file_format=None):
        """
        :param filename: the filename
        :param file_format: the file format
        """
        SaveandRetrieveModel.__init__(self, filename=filename)

    def GetModel(self):
        """
        Get the model which is saved in the file location.
        """
        if self._filename is None:
            raise Exception("Please enter the filename")
        else:
            model = sumpf.modules.SignalFile(filename=self._filename, file_format=self._file_format).GetSignal()
            label = model.GetLabels()[0]
            nonlinear_functions, aliasingcomp, aliasingcomp_loc = decode_label(label=label)
            filter_kernels = []
            for i in range(len(model.GetChannels())):
                kernel = sumpf.modules.SplitSignal(data=model, channels=[i]).GetOutput()
                filter_kernels.append(kernel)
            model = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                               filter_impulseresponses=filter_kernels,
                                               aliasing_compensation=aliasingcomp(),
                                               downsampling_position=aliasingcomp_loc)
            return model


def generate_label(nonlinearfunctions, aliasingcomp, downsamplingposition):
    """
    A helper function to generate a label based on model parameters.

    :param nonlinearfunctions: the array of nonlinear functions class
    :param aliasingcomp: the aliasing compensation class
    :param downsamplingposition: the location in which the aliasing compensation is done
    :return: the label
    """

    def fullname(o):
        return o.__module__ + "." + o.__class__.__name__

    degree = []
    nl_class = str(fullname(nonlinearfunctions[0]))
    aliasingcomp = str(fullname(aliasingcomp))
    downsamplingposition = str(downsamplingposition)
    if nl_class is nlsp.nonlinear_function.HardClip or nlsp.nonlinear_function.SoftClip:
        for nl in nonlinearfunctions:
            degree.append(nl.GetThresholds())
        degree = numpy.concatenate(numpy.array(degree), axis=0)
        degree = numpy.char.mod('%f', degree)
        degree = ",".join(degree)
        label = nl_class + "*" + degree + "*" + aliasingcomp + "*" + downsamplingposition
    else:
        for nl in nonlinearfunctions:
            degree.append(nl.GetMaximumHarmonics())
        degree = str(degree)
        label = nl_class + "*" + degree[1:-1] + "*" + aliasingcomp + "*" + downsamplingposition
    return label


def decode_label(label):
    """
    Decodes the label to different parameters of the model.

    :param label: the label
    :return: nonlinearfunctions, aliasingcomp, downsamplingposition
    """
    a = label.split('*')
    nonlinearfunction_class = a[0]
    nonlinearfunction_degree = a[1]
    aliasingcomp_type = a[2]
    aliasingcomp_loc = a[3]

    nonlinearfunction_class = eval(nonlinearfunction_class)
    if nonlinearfunction_class is nlsp.nonlinear_function.HardClip or nlsp.nonlinear_function.SoftClip:
        thres = list(eval(nonlinearfunction_degree))
        thresholds_list = []
        for a, b in zip(*[iter(thres)] * 2):
            thresholds_list.append([a,b])
        nonlinear_functions = [nonlinearfunction_class(clipping_threshold=threshold) for threshold in thresholds_list]
    else:
        nonlinearfunction_degree = [int(e) for e in nonlinearfunction_degree.split(',')]
        nonlinear_functions = [nonlinearfunction_class(degree=i) for i in nonlinearfunction_degree]
    aliasingcomp_type = eval(aliasingcomp_type)
    aliasingcomp_loc = eval(aliasingcomp_loc)
    return nonlinear_functions, aliasingcomp_type, aliasingcomp_loc
