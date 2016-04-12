

"""

@author: Eleftherios Avramidis
"""

 
from classifier import OrangeClassifier
import orange, orngLR

class LogLinear(OrangeClassifier):
    """
    classdocs
    """

    def __init__(self, data):
        self.learner = orngLR.LogRegLearner(data.get_data())
    



