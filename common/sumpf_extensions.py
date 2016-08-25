import sumpf

class SoftClipSignal(object):
    """
    Class to clip the signal using soft clipper.
    """
    def __init__(self, signal=None, thresholds=None):
        """
        :param thresholds: a tuple of thresholds to clip the signal
        :param signal: the input signal
        """
        if thresholds is None:
            thresholds = [-1.0,1.0]
            self.__power = 0
        else:
            self.__power = 1.0 - thresholds[1]
        if abs(thresholds[0]) != thresholds[1]:
            raise NotImplementedError("SoftClipSignal class only supports symmetric clipping")
        self.__thresholds = (-1.0,1.0)
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = sumpf.modules.NormalizeSignal(signal=signal).GetOutput()

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.__signal = sumpf.modules.NormalizeSignal(signal=signal).GetOutput()

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        channels = []
        for c in self.__signal.GetChannels():
            channel = []
            for s in c:
                if s <= self.__thresholds[0]:
                    channel.append(-1.0+self.__power)
                elif s >= self.__thresholds[1]:
                    channel.append(1.0-self.__power)
                else:
                    channel.append((1-abs(s)*self.__power)*s)
            channels.append(tuple(channel))
        return sumpf.Signal(channels=tuple(channels), labels=self.__signal.GetLabels())

    @sumpf.Input(tuple, "GetOutput")
    def SetThresholds(self, thresholds):
        if abs(thresholds[0]) != thresholds[1]:
            raise NotImplementedError("SoftClipSignal class only supports symmetric clipping")
        self.__power = 1.0 - thresholds[1]