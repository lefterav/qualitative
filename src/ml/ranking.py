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
    Look up in all available libraries and load ranker whose learner has a particular name
    Add here all libraries that contain a Ranker instance
    @param learner: the name of the learner that the ranker wraps around
    @type learner: str
     
    """
    from lib.scikit.ranking import SkRanker
    from lib.orange.ranking import OrangeRanker
    from ml.lib.mlp import ListNetRanker
    
    rankers = [OrangeRanker, SkRanker, ListNetRanker]   
    for ranker_class in rankers:
        ranker_instance = ranker_class(name=learner)
        try:
            ranker_instance.initialize()
            return ranker_instance 
        except Exception as e:
            logging.debug("{} replied {} ".format(ranker_class, str(e)))
            pass
    
    sys.exit("Requested ranker {} not found".format(learner))
            

class Ranker:
    '''
    Abstract base class for a machine learning algorithms that learn and apply ranking
    @ivar fit: whether the learner has been fit/trained or not
    @type fit: C{bool}
    @ivar learner: the un-trained learner class to be used for training
    @type learner: toolkit-specific C{object}  
    @ivar learner: the trained learner object
    @type learner: toolkit-specific C{object} 
    '''

    def __init__(self, learner=None, filename=None, name=None, **kwargs):
        self.fit = True
        if learner:
            self.learner = learner
        elif filename:
            model_file = open(filename)
            self.learner = pickle.load(open(filename,'r'))
            logging.info("Loaded {} learner for file {}".format(self.learner, filename))
            model_file.close()
        else:
            self.name = name
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
            try:
                logging.debug("Parallel sentence with id {}".format(parallelsentence.get_attribute("judgement_id")))
            except:
                pass
            ranked_parallelsentence, _ = self.get_ranked_sentence(parallelsentence, 
                                                                  bidirectional_pairs=bidirectional_pairs, 
                                                                  ties=True, 
                                                                  reconstruct=reconstruct,
                                                                  new_rank_name=new_rank_name)
            #write sentence with predicted ranks to the new test file
            output.add_parallelsentence(ranked_parallelsentence)
            
        output.close()        
        return {}
       
    def get_model_description(self, basename="model"):
        raise NotImplementedError()

    def get_ranked_sentence(self, parallelsentence):
        raise NotImplementedError()

    def rank_sentence(self, parallelsentence, reconstruct='hard'):
        """
        Convenience function that only returns the rank, without the parallel sentences
        @param parallelsentence: an annotated parallel sentence
        @type parallelsentence: ParallelSentence
        @return: a tuple with the ranking result and a textual description object
        @rtype: tuple of list, string
        """
        attribute_name = "rank_predicted"
        ranked_sentence, resultvector = self.get_ranked_sentence(parallelsentence, new_rank_name=attribute_name, reconstruct=reconstruct)
        result = [(t.get_attribute(attribute_name), t) for t in ranked_sentence.get_translations()]
        description = self._get_description(resultvector)
        return result, description

    def _get_description(self, vector):
        return ""

    def dump(self, dumpfilename):
        if not self.fit:
            raise AttributeError("Classifier has not been fit yet")
        pickle.dump(self.learner, open(dumpfilename, 'w'))
