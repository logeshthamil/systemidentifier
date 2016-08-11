import copy
import sumpf
import nlsp


class HGMModelGenerator():  # TODO: all classes should inherit from "object"
    """
    An abstract base class whose instances generate models.
    """
    def __init__(self, input_model, nonlinear_functions, filter_impulseresponses, aliasing_compensation, downsampling_position):
        if input_model is None:
            self.__input_model = nlsp.HammersteinGroupModel()
        else:
            self.__input_model = input_model
        if filter_impulseresponses is None:
            self.__filter_impulseresponses = self.__input_model.GetFilterImpulseResponses()
        else:
            self.__filter_impulseresponses = filter_impulseresponses
        if nonlinear_functions is None:
            self.__nonlinear_functions = self.__input_model.GetNonlinearFunctions()
        else:
            self.__nonlinear_functions = nonlinear_functions
        if aliasing_compensation is None:
            self.__aliasing_compensation = self.__input_model._get_aliasing_compensation()
        else:
            self.__aliasing_compensation = aliasing_compensation
        if downsampling_position is None:
            self.__downsampling_position = nlsp.HammersteinGroupModel.AFTER_NONLINEAR_BLOCK
        else:
            self.__downsampling_position = downsampling_position

    @sumpf.Output(nlsp.HammersteinGroupModel)
    def GetOutputModel(self):
        """
        Get the output model.
        @return: the output model
        """
        # aliasing compensation
        self.__aliasing_compensation = self.__aliasing_compensation.__class__()

        # nonlinear functions
        nl_functions = []
        for nl in self.__nonlinear_functions:
            degree = nl.GetMaximumHarmonics()
            nl_function = nl.__class__(degree=degree)
            nl_functions.append(nl_function)

        # model
        model = self.__input_model.__class__
        self.__output_model = model(nonlinear_functions=nl_functions,
                                   filter_impulseresponses=self.__filter_impulseresponses,
                                   aliasing_compensation=self.__aliasing_compensation,
                                   downsampling_position=self.__downsampling_position)
        output_model = self.__output_model
        return output_model
