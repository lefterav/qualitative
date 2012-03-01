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
        self.attributes = self._prefix_parallelsentence_attributes(ps1.get_attributes(), ps2.get_attributes())
        self._collapse_simplesentence_attributes()
        self._generate_rank()
    
    def get_couple(self):
        try:
            ref1 = self.ref[0]
            ref2 = self.ref[2]
        except:
            ref1 = None
            ref2 = None
        return (ParallelSentence(self.src[0], [self.tgt[0]], ref1, self._reconstruct_parallelsentence_attributes()[0]),
                ParallelSentence(self.src[1], [self.tgt[1]], ref2, self._reconstruct_parallelsentence_attributes()[1]))
    
    def _generate_rank(self):
        """
        Generates rank attribute after comparing the scores of the two sentences
        """
        score1 = float(self.attributes["tgt-1_score"])
        score2 = float(self.attributes["tgt-2_score"])
        if score1 < score2:
            rank = 1 
        elif score2 < score1:
            rank = -1
        else:
            rank = 0
        self.attributes["rank"] = str(rank)
    
    
    def _prefix_parallelsentence_attributes(self, attdict1, attdict2):
        """
        Merges two dicts of attributes, so that nothing gets lost and overlapping attributes get prefixed
        with the id of their original parallelsentence
        @param attdict1: dict with the attributes of the first parallelsentence
        @type attdict1: {str, str}
        @param attdict2: dict with the attributes of the second parallelsentence
        @type attdict2: {str, str}
        @return: merged dict of attributes, prefixed if necessary
        @rtype: {str, str} 
        """
        attdict_merged = {}
        
        for key in set(attdict1.keys() + attdict2.keys()):
            if not attdict1.has_key(key):
                attdict_merged[key] = attdict2[key]
            elif not attdict2.has_key(key):
                attdict_merged[key] = attdict1[key]
            elif attdict1[key] == attdict2[key]:
                attdict_merged[key] = attdict1[key]
            else:
                attdict_merged["ps1_{0}".format(key)] = attdict1[key]
                attdict_merged["ps2_{0}".format(key)] = attdict2[key]
        
        return attdict_merged
    
    def _deprefix(self, attname):
        return attname.replace("ps1_", "").replace("ps2_", "")
        
    
    def _reconstruct_parallelsentence_attributes(self):
        """
        Reverses the attributes merging that took place in _prefix_parallelsentence_attributes
        @return: two dicts containing the attributes of their respective sentences
        @rtype: ({str: str}, {str: str})
        """
        attlist1 = []
        attlist2 = []
        
        for key, value in self.attributes.iteritems():
            if not (key.startswith("ps1_") or key.startswith("ps2_")):
                attlist1.append((key, value))
                attlist2.append((key, value))
            elif key.startswith("ps1_"):
                attlist1.append((self._deprefix(key), value))
            elif key.startswith("ps2_"):
                attlist2.append((self._deprefix(key), value))
                                
        attdict1 = dict(attlist1)    
        attdict2 = dict(attlist2)
        
        return attdict1, attdict2
        

    def _collapse_simplesentence_attributes(self):
        """
        Creates a flat dictionary of attributes for the doubled parallel sentence, 
        containing attributes from its ingredients
        """
        simplesentences_prefixes = [(self.src[0], "src-1"), (self.src[1], "src-2"), (self.tgt[0], "tgt-1"), (self.tgt[1], "tgt-2")]
        
        for (simplesentence, prefix) in simplesentences_prefixes:
            
            for attribute_name, attribute_value in simplesentence.get_attributes().iteritems(): 
                prefixed_attribute_name = "{0}_{1}".format(prefix, attribute_name)
                self.attributes[prefixed_attribute_name] = attribute_value
    
    
    def get_nested_attributes(self):
        """
        Override method, since nested attributes have been already propagated up the coupled sentence
        """
        return {}
        
    
        