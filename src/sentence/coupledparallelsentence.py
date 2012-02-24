'''
Created on 23 Feb 2012

@author: lefterav
'''

from parallelsentence import ParallelSentence

class CoupledParallelSentence(ParallelSentence):
    '''
    A coupled parallelsentence contains two sources, two respective translations and their corresponding attributes
    @ivar src: a tuple containing two sources
    @type src: (L{SimpleSentence}, L{SimpleSentence})
    @ivar tgt: a tuple containing two respective translations
    @type tgt: (L{SimpleSentence}, L{SimpleSentence})
    @ivar ref: not supported 
    @type ref: None or L{SimpleSentence}
    @ivar attributes: a dict containing the attributes, as a result of merging the two sentences
    @type attributes: {str, str}
    '''


    def __init__(self, ps1, ps2):
        '''
        @param ps1: first parallel sentence of the couple
        @type ps1: L{ParallelSentence}
        @param ps2: second parallel sentence of the couple
        @type ps2: L{ParallelSentence}
        '''
        self.src = (ps1.get_source(), ps2.get_source())
        if len(ps1.get_translations()) > 1 or len(ps2.get_translations()) > 1:
            raise Exception
        self.tgt = (ps1.get_translations()[0], ps2.get_translations()[0])
        self.ref = None
        #self.ref = (ps1.get_reference()[0], ps2.get_reference()[0])
        self.attributes = {}
        self._collapse_attributes()
    
    
    def _collapse_attributes(self):
        """
        Creates a flat dictionary of attributes for the doubled parallel sentence, containing attributes from its ingredients
        """
        simplesentences_prefixes = [(self.src[0], "src-1"), (self.src[1], "src-2"), (self.tgt[0], "tgt-1"), (self.tgt[1], "tgt-2")]
        
        for (simplesentence, prefix) in simplesentences_prefixes:
            
            for attribute_name, attribute_value in simplesentence.get_attributes().iteritems(): 
                prefixed_attribute_name = "{0}_{1}".format(prefix, attribute_name)
                self.attributes[prefixed_attribute_name] = attribute_value
    
    
    def get_nested_attribute_names(self):
        """
        Override method, since nested attributes have been already propagated up the coupled sentence
        """
        return {}
        
    
        