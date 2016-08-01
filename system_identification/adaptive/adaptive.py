from system_identification.system_identification import SystemIdentification
import nlsp

class Adaptive(SystemIdentification):

    def __init__(self, excitation=None, response=None, branches=5, algorithm=None, nonlinear_function=None):
        pass