

"""

@author: Eleftherios Avramidis
"""

from orange import kNNLearner 
from classifier import OrangeClassifier

class KnnLearner(OrangeClassifier):
    """
    classdocs
    """

    def __init__(self, data):
        self.classifier = kNNLearner (data.get_data())
    



