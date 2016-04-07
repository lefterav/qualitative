"""

@author: Eleftherios Avramidis
"""

import orngTree 
from classifier import OrangeClassifier

class TreeLearner( OrangeClassifier ):
    """
    classdocs
    """


    def __init__(self, data ):
        """
        Constructor
        """
        self.learner = orngTree.TreeLearner ( data.get_data(), sameMajorityPruning=1, mForPruning=2 )