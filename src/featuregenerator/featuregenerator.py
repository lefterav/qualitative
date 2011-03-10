"""

@author: Eleftherios Avramidis
"""
from copy import deepcopy
from sentence.parallelsentence import ParallelSentence
from sentence.dataset import DataSet

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
        newset = []
        i = 0
        
        for parallelsentence in dataset.get_parallelsentences():
            
            src = self.add_features_sentence ( parallelsentence.get_source(), parallelsentence )
                        
            for tgt_item in parallelsentence.get_translations():
                tgt.append( self.add_features_sentence ( tgt_item, parallelsentence ) )
            ref = self.add_features_sentence ( parallelsentence.get_reference(), parallelsentence )
            
            ps = ParallelSentence( src, tgt, ref, parallelsentence.get_attributes() )
                                   
            ps0 = self.add_features_parallelsentence ( ps )
            
            newset.append(ps0)
            i +=1
            print i
    
        
        d = DataSet( newset )
        
        print ".",

        
        return d
    
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
    