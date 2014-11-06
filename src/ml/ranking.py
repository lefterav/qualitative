'''
Define abstract base classes that sketch the pairwise ranker behavior 
to be implemented for wrapping ML toolkits

Created on 26 Mar 2013
@author: Eleftherios Avramidis
'''
import cPickle as pickle 
import logging
import sys
from dataprocessor.ce.cejcml import CEJcmlReader
from dataprocessor.sax.saxps2jcml import IncrementalJcml

def forname(learner, **kwargs):
    """
    Look up in all available libraries and load ranker whose classifier has a particular name
    Add here all libraries that contain a Ranker instance
    @param learner: the name of the classifier that the ranker wraps around
    @type learner: str
     
    """
    from lib.orange.ranking import OrangeRanker
    from lib.scikit.ranking import SkRanker
    
    rankers = [OrangeRanker, SkRanker]   
    for ranker_class in rankers:
        ranker_instance = ranker_class(learner=learner)
        try:
            ranker_instance.initialize()
            return ranker_instance 
        except:
            pass
    
    sys.exit("Requested ranker {} not found".format(learner))
           

class Ranker:
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
            logging.info("Loaded {} classifier for file {}".format(self.classifier, filename))
            classifier_file.close()
        else:
            self.name = learner
            self.fit = False
    
    def train(self, dataset_filename, **kwargs):
        raise NotImplementedError()
    
    
    def test(self, input_filename, output_filename, reader=CEJcmlReader, writer=IncrementalJcml, 
             bidirectional_pairs=False,
             reconstruct='hard', 
             new_rank_name='rank_hard',
             **kwargs):
        """
        Use model to assign predicted ranks in a batch of parallel sentences given in an external file
        """
        #prepare an incremental reader from the input test set
        input_dataset = reader(input_filename, all_general=True, all_target=True)
        
        #sentences with predicted ranks will go into a new file
        output = writer(output_filename)
        
        #iterate over given test sentences
        for parallelsentence in input_dataset.get_parallelsentences():
#             #original tested sentences should not have ties 
#             parallelsentence.remove_ties()
            #get the same sentence with predicted ranks assigned
            ranked_parallelsentence, _ = self.get_ranked_sentence(parallelsentence, 
                                                                  bidirectional_pairs=bidirectional_pairs, 
                                                                  ties=True, 
                                                                  reconstruct=reconstruct,
                                                                  new_rank_name=new_rank_name)
            #write sentence with predicted ranks to the new test file
            output.add_parallelsentence(ranked_parallelsentence)
            
        output.close()        
        return {}
    #------------------------------ def train(self, dataset_filename, **kwargs):
        # pairwise_dataset_filename = dataset_filename.replace(".jcml", ".pair.jcml")
        # pairwise_ondisk(dataset_filename, pairwise_dataset_filename, **kwargs)
        #---------- super(Ranker, self).train(pairwise_dataset_filename)
        #----- #self.classifier = Ranker(classifier=pairwise_classifier)
#------------------------------------------------------------------------------ 
    def get_model_description(self, basename="model"):
        raise NotImplementedError()

    def get_ranked_sentence(self, parallelsentence):
        raise NotImplementedError()

    def dump(self, dumpfilename):
        if not self.fit:
            raise AttributeError("Classifier has not been fit yet")
        pickle.dump(self.classifier, open(dumpfilename, 'w'))
