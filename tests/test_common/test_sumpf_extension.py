import sumpf
import nlsp

def test_softclipper():
    """
    Test whether the soft clipper class works.
    """
    soft_clipper = nlsp.sumpf.SoftClipSignal(thresholds=[-1.1,1.1])
    test_signal = sumpf.modules.SweepGenerator().GetSignal()
    soft_clipper.SetInput(test_signal)
    soft_clipper.GetOutput()