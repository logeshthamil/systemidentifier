import sumpf
import nlsp

class HammersteinGroupModel(object):
    """
    A class to construct a Hammerstein Group Model.
    """
    def __init__(self, input_signal=None, nonlinear_functions=None, filter_impulseresponses=None,
                 aliasing_compensation=None, downsampling_position=None):
        """
        @param input_signal: the input signal
        @param nonlinear_functions: the nonlinear functions Eg. [nonlinear_function1, nonlinear_function2, ...]
        @param filter_impulseresponse: the filter impulse responses Eg. [impulse_response1, impulse_response2, ...]
        @param aliasing_compensation: the aliasin compensation technique
        Eg. nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
        @param downsampling_position: the downsampling position, Eg. 1 for downsampling immediately after the nonlinear
        block and 2 for downsampling after the filter processing
        """
        pass

    def GetFilterImpulseResponses(self):
        """
        Get the filter impulse responses.
        @return: the filter impulse responses
        """
        pass

    def GetNonlinearFunctions(self):
        """
        Get the nonlinear functions.
        @return: the nonlinear functions
        """
        pass

    def SetInput(self, input_signal=None):
        """
        Set the input to the model.
        @param input_signal: the input signal
        """
        pass

    def GetOutput(self):
        """
        Get the output signal of the model.
        @return: the output signal
        """
        pass

class HammersteinModel(object):
    """
    A class to construct a Hammerstein model.
    """
    def __init__(self, input_signal=None, nonlinear_function=None, filter_impulseresponse=None,
                 aliasing_compensation=None):
        """
        :param input_signal: the input signal
        :param nonlinear_function: the nonlinear function
        :param filter_impulseresponse: the impulse response
        :param aliasing_compensation: the aliasing compensation technique
        """
        # interpret the input parameters
        if input_signal is None:
            self._input_signal = sumpf.Signal()
        else:
            self._input_signal = input_signal
        if filter_impulseresponse is None:
            self._filterir     = sumpf.modules.ImpulseGenerator(length=len(input_signal),
                                                            samplingrate=input_signal.GetSamplingRate()).GetSignal()
        else:
            self._filterir     = filter_impulseresponse
        if nonlinear_function is None:
            self._nonlin_func  = nlsp.nonlinear.Powerseries(degree=1)
        else:
            self._nonlin_func      = nonlinear_function
        if aliasing_compensation is None:
            self._signalaliascomp  = nlsp.aliasing_compensation.NoAliasingCompensation()
        else:
            self._signalaliascomp  = aliasing_compensation

        # downsampling placement
        self._downsampling_position = self._signalaliascomp._GetDownsamplingPosition()
        if self._downsampling_position == 1:
            self._filteraliascomp = nlsp.aliasing_compensation.NoAliasingCompensation()
            self._signalaliascomp1 = self._signalaliascomp
            self._signalaliascomp2 = nlsp.aliasing_compensation.NoAliasingCompensation()
        elif self._downsampling_position == 2:
            self._filteraliascomp = self._signalaliascomp
            self._signalaliascomp2 = self._signalaliascomp
            self._signalaliascomp1 = nlsp.aliasing_compensation.NoAliasingCompensation()

        # set up the signal processing objects
        self._passsignal    = sumpf.modules.PassThroughSignal(signal=self._input_signal)
        self._passfilter    = sumpf.modules.PassThroughSignal(signal=self._filterir)
        self._transform     = sumpf.modules.FourierTransform()
        self._itransform    = sumpf.modules.InverseFourierTransform()
        self._splitsignalspec   = sumpf.modules.SplitSpectrum(channels=[0])
        self._splitfilterspec   = sumpf.modules.SplitSpectrum(channels=[1])
        self._merger  = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        self._multiplier    = sumpf.modules.Multiply()

        # define input and output methods
        self.SetInput  = self._passsignal.SetSignal
        self.GetOutput = self._signalaliascomp2.GetPostprocessingOutput

        # connect the signal processing objects
        self._Connect()

    def _Connect(self):
        sumpf.connect(self._passsignal.GetSignal, self._signalaliascomp.SetPreprocessingInput)
        sumpf.connect(self._signalaliascomp.GetPreprocessingOutput(), self._nonlin_func.SetInput)
        sumpf.connect(self._nonlin_func.GetOutput, self._signalaliascomp1.SetPostprocessingInput)
        sumpf.connect(self._signalaliascomp1.GetPreprocessingOutput, self._merger.AddInput)
        sumpf.connect(self._passfilter.GetSignal, self._filteraliascomp.SetPreprocessingInput)
        sumpf.connect(self._filteraliascomp.GetPreprocessingOutput, self._merger.AddInput)
        sumpf.connect(self._merger.GetOutput, self._transform.SetSignal)
        sumpf.connect(self._transform.GetSpectrum, self._splitsignalspec.SetInput)
        sumpf.connect(self._splitsignalspec.GetOutput, self._multiplier.SetValue1)
        sumpf.connect(self._splitfilterspec.GetOutput, self._multiplier.SetValue2)
        sumpf.connect(self._multiplier.GetResult, self._itransform.SetSpectrum)
        sumpf.connect(self._itransform.GetSignal, self._signalaliascomp2.SetPostprocessingInput)
