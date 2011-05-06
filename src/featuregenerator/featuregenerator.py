"""

@author: Eleftherios Avramidis
"""
from copy import deepcopy
from sentence.parallelsentence import ParallelSentence
from sentence.dataset import DataSet
from io.input.xmlreader import XmlReader
from io.output.xmlwriter import XmlWriter

class FeatureGenerator(object):
    """
    classdocs
    """
    

    def __init__(self):
        """
        Constructor
        """
        

    def add_features(self, dataset):
        """
        Fires the oo nested feature generation processes by parallelsentence and simplesentence
        
        """
        tgt=[]
        parallelsentences = dataset.get_parallelsentences()
        
        for i in range(len(parallelsentences)):
            parallelsentence = parallelsentences[i]
             
        #for parallelsentence in dataset.get_parallelsentences():
            
            src = self.add_features_sentence (parallelsentence.get_source(), parallelsentence)
                        
            for tgt_item in parallelsentence.get_translations():
                tgt.append( self.add_features_sentence (tgt_item, parallelsentence))
            ref = self.add_features_sentence (parallelsentence.get_reference(), parallelsentence)
            
            #replace the parallelsentence
            parallelsentences[i] = ParallelSentence(src, tgt, ref, parallelsentence.get_attributes())
                                   
            #ps0 = self.add_features_parallelsentence ( ps )
            
            #newset.append(ps0)
            print i
    
        
        dataset = DataSet(parallelsentences)
        
        print ".",

        
        return dataset
    
    def add_features_src(self,simplesentence, parallelsentence):
        return self.add_features_sentence(simplesentence, parallelsentence)

    def add_features_tgt(self,simplesentence, parallelsentence):
        return self.add_features_sentence(simplesentence, parallelsentence)
    
    def add_features_sentence(self, simplesentence, parallelsentence):
        ss = deepcopy( simplesentence )
        newfeatures = self.get_features_sentence( ss, parallelsentence )
        ss.add_attributes( newfeatures )
        return ss
        
    def add_features_parallelsentence(self, parallelsentence):
        ps = deepcopy( parallelsentence )
        ps.add_attributes ( self.get_features_parallelsentence( parallelsentence ) )
        return ps
    
    def get_features_sentence(self, ss, ps):
        emptydict = {}
        return emptydict
    
    def get_features_parallelsentence(self, ps):
        emptydict = {}
        return emptydict
    
    def add_features_batch(self, parallelsentences):
        #Default function, if not overriden
        self.add_features(DataSet(parallelsentences))
        
    def add_features_batch_xml(self, filename_in, filename_out):
        reader = XmlReader(filename_in)
        parallelsentences = reader.get_parallelsentences()
        parallelsentences = self.add_features_batch(parallelsentences)
        reader = None
        writer = XmlWriter(parallelsentences)
        writer.write_to_file(filename_out)
        
        