"""

@author: Eleftherios Avramidis
"""

from sentence.parallelsentence import ParallelSentence

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
        
        for parallelsentence in dataset.get_parallelsentences():
            
            src = self.add_features_sentence ( parallelsentence.get_source(), parallelsentence )
            for tgt_item in parallelsentence.get_translations():
                tgt.append( self.add_features_sentence ( tgt_item, parallelsentence ) )
            ref = self.add_features_sentence ( parallelsentence.get_reference(), parallelsentence )
            
            ps = ParallelSentence( src, tgt, ref, parallelsentence.get_attributes() )            
            ps = self.add_features_parallelsentence ( parallelsentence )
                    
        return ps
    
    def add_features_sentence(self, simplesentence, parallelsentence):
        simplesentence.add_attributes( self.get_features_sentence() )
        
    def add_features_parallelsentence(self, parallelsentence):
        parallelsentence.add_attributes ( self.get_features_parallelsentence() )
    
    
    