
class NonlinearFunction(object):
    def __init__(self):
        pass

    def SetInput(self):
        pass

    def GetOutput(self):
        pass

    def GetMaximumHarmonics(self):
        pass

class PolynomialNonlinearFunction(NonlinearFunction):
    def __init__(self):
        pass

    def SetDegree(self):
        pass

class PowerseriesNonlinearFunction(PolynomialNonlinearFunction):
    def __init__(self, signal=None, degree=None):
        pass

class ChebyshevNonlinearFunction(PolynomialNonlinearFunction):
    def __init__(self, signal=None, degree=None):
        pass

class HermiteNonlinearFunction(PolynomialNonlinearFunction):
    def __init__(self, signal=None, degree=None):
        pass

class LegendreNonlinearFunction(PolynomialNonlinearFunction):
    def __init__(self, signal=None, degree=None):
        pass

class ClippingNonlinearFunction(NonlinearFunction):
    def __init__(self, signal=None, thresholds=None, maximum_harmonics=None):
        pass

    def SetThreshold(self):
        pass