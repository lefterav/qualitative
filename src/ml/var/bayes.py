

"""

@author: Eleftherios Avramidis
"""

from orange import BayesLearner 
from classifier import OrangeClassifier

class Bayes( OrangeClassifier ):
    """
    classdocs
    """

    def __init__(self, data):
        self.learner = BayesLearner ( data.get_data() )
    



