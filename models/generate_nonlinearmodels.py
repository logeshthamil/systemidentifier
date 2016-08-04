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
            self.__filter_irs = (sumpf.modules.ImpulseGenerator(samplingrate=self.__input_signal.GetSamplingRate(),length=len(self.__input_signal)).GetSignal(),)*len(self.__nonlinear_functions)
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
        aliasing_comp = []
        while len(aliasing_comp) != self.__branches:
            classname = self.__aliasingcompensation.__class__
            aliasing_comp.append(classname())
        self.__aliasingcompensation = aliasing_comp

        # construct HGM from given paramters
        self.__constructHGM()

    def __constructHGM(self):
        self.__hmodels = []
        for i,(nl,ir,alias) in enumerate(zip(self.__nonlinear_functions, self.__filter_irs, self.__aliasingcompensation)):
            h = HammersteinModel(input_signal=self.__passsignal.GetSignal(), nonlinear_function=nl,
                                 filter_impulseresponse=ir, aliasing_compensation=alias)
            self.__hmodels.append(h)

    @sumpf.Output(tuple)
    def GetFilterImpulseResponses(self):
        return self.__filter_irs

    @sumpf.Output(tuple)
    def GetNonlinearFunctions(self):
        return self.__nonlinear_functions

    @sumpf.Input(data_type=sumpf.Signal,observers=["__constructHGM","GetOutput"])
    def SetInput(self, input_signal=None):
        """
        Set the input to the model.
        @param input_signal: the input signal
        """
        self.__passsignal.SetSignal(signal=input_signal)

    @sumpf.Output(data_type=sumpf.Signal)
    def GetOutput(self):
        """
        Get the output signal of the model.
        @return: the output signal
        """
        self.__sums = [None] * self.__branches
        for i in reversed(range(len(self.__hmodels)-1)):
            self.__a = sumpf.modules.Add()
            # print "connecting hammerstein model %i to adder %i" % (i, i)
            sumpf.connect(self.__hmodels[i].GetOutput, self.__a.SetValue1)
            if i == len(self.__hmodels)-2:
                # print "connecting hammerstein model %i to adder %i" % (i+1, i)
                sumpf.connect(self.__hmodels[i+1].GetOutput, self.__a.SetValue2)
            else:
                # print "connecting adder %i to adder %i" % (i+1, i)
                sumpf.connect(self.__sums[i+1].GetOutput, self.__a.SetValue2)
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
            self.__input_signal = sumpf.Signal()
        else:
            self.__input_signal = input_signal
        if filter_impulseresponse is None:
            self.__filterir     = sumpf.modules.ImpulseGenerator(length=len(input_signal),
                                                            samplingrate=input_signal.GetSamplingRate()).GetSignal()
        else:
            self.__filterir     = filter_impulseresponse
        if nonlinear_function is None:
            self.__nonlin_func  = nlsp.nonlinear_functions.Power(degree=1)
        else:
            self.__nonlin_func      = nonlinear_function
        if aliasing_compensation is None:
            self.__signalaliascomp  = nlsp.aliasing_compensation.NoAliasingCompensation()
        else:
            self.__signalaliascomp  = aliasing_compensation

        # downsampling placement
        self.__downsampling_position = self.__signalaliascomp._GetDownsamplingPosition()
        if self.__downsampling_position == 1:
            self.__filteraliascomp = nlsp.aliasing_compensation.NoAliasingCompensation()
            self.__signalaliascomp1 = self.__signalaliascomp
            self.__signalaliascomp2 = nlsp.aliasing_compensation.NoAliasingCompensation()
        elif self.__downsampling_position == 2:
            self.__filteraliascomp = self.__signalaliascomp.__class__()
            self.__signalaliascomp2 = self.__signalaliascomp
            self.__signalaliascomp1 = nlsp.aliasing_compensation.NoAliasingCompensation()

        # set up the signal processing objects
        self.__passsignal    = sumpf.modules.PassThroughSignal(signal=self.__input_signal)
        self.__passfilter    = sumpf.modules.PassThroughSignal(self.__filterir)
        self.__transform     = sumpf.modules.FourierTransform()
        self.__itransform    = sumpf.modules.InverseFourierTransform()
        self.__splitsignalspec   = sumpf.modules.SplitSpectrum(channels=[0])
        self.__splitfilterspec   = sumpf.modules.SplitSpectrum(channels=[1])
        self.__merger  = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        self.__multiplier    = sumpf.modules.Multiply()

        # define input and output methods
        self.SetInput  = self.__passsignal.SetSignal
        self.GetOutput = self.__signalaliascomp2.GetPostprocessingOutput

        # connect the signal processing objects
        self.__Connect()

    def __Connect(self):
        sumpf.connect(self.__nonlin_func.GetMaximumHarmonics, self.__signalaliascomp.SetMaximumHarmonics)
        sumpf.connect(self.__nonlin_func.GetMaximumHarmonics, self.__filteraliascomp.SetMaximumHarmonics)
        sumpf.connect(self.__passsignal.GetSignal, self.__signalaliascomp.SetPreprocessingInput)
        sumpf.connect(self.__signalaliascomp.GetPreprocessingOutput, self.__nonlin_func.SetInput)
        sumpf.connect(self.__nonlin_func.GetOutput, self.__signalaliascomp1.SetPostprocessingInput)
        sumpf.connect(self.__signalaliascomp1.GetPostprocessingOutput, self.__merger.AddInput)
        sumpf.connect(self.__passfilter.GetSignal, self.__filteraliascomp.SetPreprocessingInput)
        sumpf.connect(self.__filteraliascomp.GetPreprocessingOutput, self.__merger.AddInput)
        sumpf.connect(self.__merger.GetOutput, self.__transform.SetSignal)
        sumpf.connect(self.__transform.GetSpectrum, self.__splitsignalspec.SetInput)
        sumpf.connect(self.__transform.GetSpectrum, self.__splitfilterspec.SetInput)
        sumpf.connect(self.__splitsignalspec.GetOutput, self.__multiplier.SetValue1)
        sumpf.connect(self.__splitfilterspec.GetOutput, self.__multiplier.SetValue2)
        sumpf.connect(self.__multiplier.GetResult, self.__itransform.SetSpectrum)
        sumpf.connect(self.__itransform.GetSignal, self.__signalaliascomp2.SetPostprocessingInput)
