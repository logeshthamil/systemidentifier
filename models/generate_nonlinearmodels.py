import sumpf
import nlsp


class HammersteinGroupModel(object):
    """
    A class to construct a Hammerstein Group Model.
    """

    def __init__(self, input_signal=None, nonlinear_functions=None, filter_impulseresponses=None,
                 aliasing_compensation=None):
        """
        @param input_signal: the input signal
        @param nonlinear_functions: the nonlinear functions Eg. [nonlinear_function1, nonlinear_function2, ...]
        @param filter_impulseresponse: the filter impulse responses Eg. [impulse_response1, impulse_response2, ...]
        @param aliasing_compensation: the aliasin compensation technique
        Eg. nlsp.aliasing_compensation.FullUpsamplingAliasingCompensation()
        """
        # interpret the input parameters
        if input_signal is None:
            self.__input_signal = sumpf.Signal()
        else:
            self.__input_signal = input_signal
        if nonlinear_functions is None:
            self.__nonlinear_functions = (nlsp.nonlinear_functions.Power(degree=1),)
        else:
            self.__nonlinear_functions = nonlinear_functions
        if filter_impulseresponses is None:
            self.__filter_irs = (sumpf.modules.ImpulseGenerator(samplingrate=self.__input_signal.GetSamplingRate(),
                                                                length=len(self.__input_signal)).GetSignal(),) * len(
                self.__nonlinear_functions)
        else:
            self.__filter_irs = filter_impulseresponses

        # check if the filter ir length and the nonlinear functions length is same
        if len(self.__nonlinear_functions) == len(self.__filter_irs):
            self.__branches = len(self.__nonlinear_functions)
        else:
            print "the given arguments dont have same length"
        self.__passsignal = sumpf.modules.PassThroughSignal(signal=self.__input_signal)

        # create multiple aliasing compensation instances which is similar to the aliasing compensation parameter received
        if aliasing_compensation is None:
            self.__aliasingcompensation = nlsp.aliasing_compensation.NoAliasingCompensation()
        else:
            self.__aliasingcompensation = aliasing_compensation
        self.__downsampling_position = self.__aliasingcompensation._downsampling_position

        aliasing_comp = []
        while len(aliasing_comp) != self.__branches:
            classname = self.__aliasingcompensation.__class__()
            classname._SetDownsamplingPosition(self.__downsampling_position)
            aliasing_comp.append(classname)
        self.__aliasingcompensations = aliasing_comp

        # construct HGM from given paramters
        self._constructHGM()

    def _constructHGM(self):
        self.__hmodels = []
        for i, (nl, ir, alias) in enumerate(
                zip(self.__nonlinear_functions, self.__filter_irs, self.__aliasingcompensations)):
            h = HammersteinModel(input_signal=self.__passsignal.GetSignal(), nonlinear_function=nl,
                                 filter_impulseresponse=ir, aliasing_compensation=alias)
            self.__hmodels.append(h)

    def _get_aliasing_compensation(self):
        return self.__aliasingcompensation

    @sumpf.Output(tuple)
    def GetFilterImpulseResponses(self):
        return self.__filter_irs

    def GetNonlinearFunctions(self):
        return self.__nonlinear_functions

    @sumpf.Input(data_type=sumpf.Signal)
    def SetInput(self, input_signal=None):
        """
        Set the input to the model.
        @param input_signal: the input signal
        """
        inputs = []
        for i in range(len(self.__hmodels)):
            inputs.append((self.__hmodels[i].SetInput, input_signal))
        sumpf.set_multiple_values(inputs)

    @sumpf.Output(data_type=sumpf.Signal)
    def GetOutput(self):
        """
        Get the output signal of the model.
        @return: the output signal
        """
        self.__sums = [None] * self.__branches
        for i in reversed(range(len(self.__hmodels) - 1)):
            self.__a = sumpf.modules.Add()
            # print "connecting hammerstein model %i to adder %i" % (i, i)
            sumpf.connect(self.__hmodels[i].GetOutput, self.__a.SetValue1)
            if i == len(self.__hmodels) - 2:
                # print "connecting hammerstein model %i to adder %i" % (i+1, i)
                sumpf.connect(self.__hmodels[i + 1].GetOutput, self.__a.SetValue2)
            else:
                # print "connecting adder %i to adder %i" % (i+1, i)
                sumpf.connect(self.__sums[i + 1].GetResult, self.__a.SetValue2)
            self.__sums[i] = self.__a
        if len(self.__hmodels) == 1:
            self.__sums[0] = self.__hmodels[0]
            return self.__sums[0].GetOutput()
        else:
            return self.__sums[0].GetResult()


class HammersteinModel(object):
    """
    A class to construct a Hammerstein model.
    """
    AFTER_NONLINEAR_BLOCK = 1
    AFTER_LINEAR_BLOCK = 2

    def __init__(self, input_signal=None, nonlinear_function=None, filter_impulseresponse=None,
                 aliasing_compensation=None, downsampling_position=AFTER_NONLINEAR_BLOCK):
        """
        :param input_signal: the input signal
        :param nonlinear_function: the nonlinear function
        :param filter_impulseresponse: the impulse response
        :param aliasing_compensation: the aliasing compensation technique
        :param downsampling_position: the downsampling position Eg. AFTER_NONLINEAR_BLOCK or AFTER_LINEAR_BLOCK
        """
        # interpret the input parameters
        self.__ir = filter_impulseresponse
        if input_signal is None:
            self.__input_signal = sumpf.modules.ConstantSignalGenerator(value=0.0, length=2**16).GetSignal()
        else:
            self.__input_signal = input_signal
        self.__passsignal = sumpf.modules.PassThroughSignal(signal=self.__input_signal)

        if filter_impulseresponse is None:
            self.__filterir = sumpf.modules.ImpulseGenerator(samplingrate=self.__input_signal.GetSamplingRate(),
                                                             length=int(len(self.__input_signal)/2.0)).GetSignal()
        else:
            self.__filterir = self.__ir
        self.__passfilter = sumpf.modules.PassThroughSignal(self.__filterir)

        if nonlinear_function is None:
            self.__nonlin_function = nlsp.nonlinear_functions.Power(degree=1)
        else:
            self.__nonlin_function = nonlinear_function
        if aliasing_compensation is None:
            self.__signalaliascomp = nlsp.aliasing_compensation.NoAliasingCompensation()
        else:
            self.__signalaliascomp = aliasing_compensation
        self.__downsampling_position = downsampling_position

        # connect different signal processing blocks based on downsampling position
        if self.__downsampling_position == 1:
            # set up the signal processing objects
            self.__prop_signal = sumpf.modules.ChannelDataProperties()
            self.__prop_filter = sumpf.modules.ChannelDataProperties()
            self.__subtract = sumpf.modules.Subtract()
            self.__generatezeros = sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=self.__prop_signal.GetSamplingRate())
            self.__concatenate = sumpf.modules.ConcatenateSignals()
            self.__resampler = sumpf.modules.ResampleSignal()
            self.__transform_signal = sumpf.modules.FourierTransform()
            self.__transform_filter = sumpf.modules.FourierTransform()
            self.__multiplier = sumpf.modules.Multiply()
            self.__itransform = sumpf.modules.InverseFourierTransform()
            self.__passoutput = sumpf.modules.PassThroughSignal()
            self.__connect1()

        elif self.__downsampling_position == 2:
            # set up the signal processing objects
            self.__prop_signal = sumpf.modules.ChannelDataProperties()
            self.__prop_filter = sumpf.modules.ChannelDataProperties()
            self.__subtract = sumpf.modules.Subtract()
            self.__generatezeros = sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=self.__prop_signal.GetSamplingRate())
            self.__concatenate = sumpf.modules.ConcatenateSignals()
            self.__resampler = sumpf.modules.ResampleSignal()
            self.__transform_signal = sumpf.modules.FourierTransform()
            self.__transform_filter = sumpf.modules.FourierTransform()
            self.__multiplier = sumpf.modules.Multiply()
            self.__itransform = sumpf.modules.InverseFourierTransform()
            self.__passoutput = sumpf.modules.PassThroughSignal()
            self.__connect2()

        # define input and output methods
        self.SetInput = self.__passsignal.SetSignal
        self.GetOutput = self.__passoutput.GetSignal

    def __connect1(self):
        sumpf.connect(self.__nonlin_function.GetMaximumHarmonics, self.__signalaliascomp.SetMaximumHarmonics)
        sumpf.connect(self.__passsignal.GetSignal, self.__signalaliascomp.SetPreprocessingInput)
        sumpf.connect(self.__signalaliascomp.GetPreprocessingOutput, self.__nonlin_function.SetInput)
        sumpf.connect(self.__nonlin_function.GetOutput, self.__signalaliascomp.SetPostprocessingInput)
        sumpf.connect(self.__signalaliascomp.GetPostprocessingOutput, self.__prop_signal.SetSignal)
        sumpf.connect(self.__prop_signal.GetSignalLength, self.__subtract.SetValue1)
        sumpf.connect(self.__prop_signal.GetSamplingRate, self.__resampler.SetSamplingRate)
        sumpf.connect(self.__passfilter.GetSignal, self.__resampler.SetInput)
        sumpf.connect(self.__resampler.GetOutput, self.__prop_filter.SetSignal)
        sumpf.connect(self.__prop_filter.GetSignalLength, self.__subtract.SetValue2)
        sumpf.connect(self.__prop_filter.GetSamplingRate, self.__generatezeros.SetSamplingRate)
        sumpf.connect(self.__subtract.GetResult, self.__generatezeros.SetLength)
        sumpf.connect(self.__resampler.GetOutput, self.__concatenate.SetInput1)
        sumpf.connect(self.__generatezeros.GetSignal, self.__concatenate.SetInput2)
        sumpf.connect(self.__concatenate.GetOutput, self.__transform_filter.SetSignal)
        sumpf.connect(self.__signalaliascomp.GetPostprocessingOutput, self.__transform_signal.SetSignal)
        sumpf.connect(self.__transform_signal.GetSpectrum, self.__multiplier.SetValue1)
        sumpf.connect(self.__transform_filter.GetSpectrum, self.__multiplier.SetValue2)
        sumpf.connect(self.__multiplier.GetResult, self.__itransform.SetSpectrum)
        sumpf.connect(self.__itransform.GetSignal, self.__passoutput.SetSignal)

    def __connect2(self):
        sumpf.connect(self.__nonlin_function.GetMaximumHarmonics, self.__signalaliascomp.SetMaximumHarmonics)
        sumpf.connect(self.__passsignal.GetSignal, self.__signalaliascomp.SetPreprocessingInput)
        sumpf.connect(self.__signalaliascomp.GetPreprocessingOutput, self.__nonlin_function.SetInput)
        sumpf.connect(self.__nonlin_function.GetOutput, self.__prop_signal.SetSignal)
        sumpf.connect(self.__prop_signal.GetSignalLength, self.__subtract.SetValue1)
        sumpf.connect(self.__prop_signal.GetSamplingRate, self.__resampler.SetSamplingRate)
        sumpf.connect(self.__passfilter.GetSignal, self.__resampler.SetInput)
        sumpf.connect(self.__resampler.GetOutput, self.__prop_filter.SetSignal)
        sumpf.connect(self.__prop_filter.GetSignalLength, self.__subtract.SetValue2)
        sumpf.connect(self.__prop_filter.GetSamplingRate, self.__generatezeros.SetSamplingRate)
        sumpf.connect(self.__subtract.GetResult, self.__generatezeros.SetLength)
        sumpf.connect(self.__resampler.GetOutput, self.__concatenate.SetInput1)
        sumpf.connect(self.__generatezeros.GetSignal, self.__concatenate.SetInput2)
        sumpf.connect(self.__concatenate.GetOutput, self.__transform_filter.SetSignal)
        sumpf.connect(self.__nonlin_function.GetOutput, self.__transform_signal.SetSignal)
        sumpf.connect(self.__transform_signal.GetSpectrum, self.__multiplier.SetValue1)
        sumpf.connect(self.__transform_filter.GetSpectrum, self.__multiplier.SetValue2)
        sumpf.connect(self.__multiplier.GetResult, self.__itransform.SetSpectrum)
        sumpf.connect(self.__itransform.GetSignal, self.__signalaliascomp.SetPostprocessingInput)
        sumpf.connect(self.__signalaliascomp.GetPostprocessingOutput, self.__passoutput.SetSignal)
