import sumpf
import nlsp


class HGMModelGenerator():  # TODO: all classes should inherit from "object"
    """
    An abstract base class whose instances generate models.
    """
    def __init__(self, input_model=None, nonlinear_functions=None, filter_impulseresponses=None, aliasing_compensation=None,
                 downsampling_position=None):
        """
        @param input_model: the input model
        @param filter_impulseresponses: the filter impulse responses
        Eg. [filter_impulseresponse1, filter_impulseresponse2, ...]
        @param nonlinear_function: the nonlinear functions
        Eg. [nonlinear_function1, nonlinear_function2, ...]
        @param aliasing_compensation: the aliasing compensation technique
        Eg. nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
        @param downsampling_position: the downsampling position in the HGM
        """
        if input_model is None:
            self._input_model = nlsp.HammersteinGroupModel()
        else:
            self._input_model = input_model

        if nonlinear_functions is None:
            self._nonlinear_functions = self._input_model.GetNonlinearFunctions()
        else:
            self._nonlinear_functions = nonlinear_functions

        if filter_impulseresponses is None:
            self._filter_impulseresponses = self._input_model.GetFilterImpulseResponses()
        else:
            self._filter_impulseresponses = filter_impulseresponses

        if aliasing_compensation is None:
            self._aliasing_compensation = self._input_model._get_aliasing_compensation()
        else:
            self._aliasing_compensation = aliasing_compensation

        if downsampling_position is None:
            self._downsampling_position = self._input_model._downsampling_position
        else:
            self._downsampling_position = downsampling_position

    @sumpf.Output(nlsp.HammersteinGroupModel)
    def GetOutputModel(self):
        """
        Get the output model.
        @return: the output model
        """
        # aliasing compensation
        self._aliasing_compensation = self._aliasing_compensation.CreateModified()

        # nonlinear functions
        nl_functions = []
        for nl in self._nonlinear_functions:
            nl_function = nl.CreateModified()
            nl_functions.append(nl_function)

        # model
        model = self._input_model.__class__
        self.__output_model = model(nonlinear_functions=nl_functions,
                                    filter_impulseresponses=self._filter_impulseresponses,
                                    aliasing_compensation=self._aliasing_compensation,
                                    downsampling_position=self._downsampling_position)
        output_model = self.__output_model
        return output_model
