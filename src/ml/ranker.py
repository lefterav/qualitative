'''
Define abstract base classes that sketch the pairwise ranker behavior 
to be implemented for wrapping ML toolkits

Created on 26 Mar 2013
@author: Eleftherios Avramidis
'''
import cPickle as pickle 

class PairwiseRanker:
    '''
    Abstract base class for a machine learning algorithms that learn and apply ranking
    @ivar fit: whether the classifier has been fit/trained or not
    @type fit: C{bool}
    @ivar learner: the un-trained classifier class to be used for training
    @type learner: toolkit-specific C{object}  
    @ivar classifier: the trained classifier object
    @type classifier: toolkit-specific C{object} 
    '''
    def __init__(self, classifier=None, filename=None, learner=None, **kwargs):
        self.fit = True
        if classifier:
            self.classifier = classifier
        elif filename:
            classifier_file = open(filename)
            self.classifier = pickle.load(open(filename,'r'))
            classifier_file.close()
        else:
            self.learner = learner
            self.fit = False
    
    def train(self, dataset_filename, **kwargs):
        raise NotImplementedError()
    #------------------------------ def train(self, dataset_filename, **kwargs):
        # pairwise_dataset_filename = dataset_filename.replace(".jcml", ".pair.jcml")
        # pairwise_ondisk(dataset_filename, pairwise_dataset_filename, **kwargs)
        #---------- super(PairwiseRanker, self).train(pairwise_dataset_filename)
        #----- #self.classifier = PairwiseRanker(classifier=pairwise_classifier)
#------------------------------------------------------------------------------ 
    
    def get_ranked_sentence(self, parallelsentence):
        raise NotImplementedError()
