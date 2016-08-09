import sumpf
import nlsp

class HGMModelGenerator():  # TODO: all classes should inherit from "object"
    """
    An abstract base class whose instances generate models.
    """
    # TODO: again no constructor, but the methods access attributes (see the AliasingCompensation class)

    @sumpf.Output(nlsp.HammersteinGroupModel)
    def GetOutputModel(self):
        """
        Get the output model.
        @return: the output model
        """
        # aliasing compensation
        downsampling_position = self._aliasing_compensation._downsampling_position
        self._aliasing_compensation = self._aliasing_compensation.__class__()
        self._aliasing_compensation._SetDownsamplingPosition(downsampling_position=downsampling_position)

        # nonlinear functions
        nl_functions = []
        for nl in self._nonlinear_functions:
            degree = nl.GetMaximumHarmonics()
            nl_function = nl.__class__(degree=degree)
            nl_functions.append(nl_function)

        # model
        model = self._input_model.__class__
        self._output_model = model(nonlinear_functions=nl_functions,
                                   filter_impulseresponses=self._filter_impulseresponses,
                                   aliasing_compensation=self._aliasing_compensation)
        output_model = self._output_model
        return output_model
