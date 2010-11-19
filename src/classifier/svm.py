'''

@author: Eleftherios Avramidis
'''

from orange import SVMLearner
from classifier import OrangeClassifier


class SVM( OrangeClassifier ):
    '''
    classdocs
    '''


    def __init__(self, data):
        '''
        Constructor
        '''
        l = SVMLearner() 
        l.svm_type = SVMLearner.Nu_SVC 
        l.nu = 0.3 
        l.probability = True
        self.classifier = l( data.get_data() )
        