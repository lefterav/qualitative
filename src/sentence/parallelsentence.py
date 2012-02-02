#!/usr/bin/python
# -*- coding: utf-8 -*-


"""

@author: Eleftherios Avramidis
"""

from copy import deepcopy
import re
import sys

class ParallelSentence(object):
    """
    classdocs
    """
    

    def __init__(self, source, translations, reference = None, attributes = {}):
        """
        Constructor
        @type source SimpleSentence
        @param source The source text of the parallel sentence
        @type translations list ( SimpleSentence )
        @param translations A list of given translations
        @type reference SimpleSentence 
        @param reference The desired translation provided by the system
        @type attributes dict { String name , String value }
        @param the attributes that describe the parallel sentence
        """
        self.src = source 
        self.tgt = translations
        self.ref = reference
        self.attributes = deepcopy (attributes)
    
    def get_attributes (self):
        return self.attributes
    
    def get_attribute_names (self):
        return self.attributes.keys()
    
    def get_attribute(self, name):
        return self.attributes[name]
    
    def get_target_attribute_values(self, attribute_name):
        attribute_values = []
        for target in self.tgt:
            attribute_values.append(target.get_attribute(attribute_name))
        return attribute_values

    def add_attributes(self, attributes):
        self.attributes.update( attributes )
    
    def set_langsrc (self, langsrc):
        self.attributes["langsrc"] = langsrc

    def set_langtgt (self, langtgt):
        self.attributes["langtgt"] = langtgt
        
    def set_id (self, id):
        self.attributes["id"] = str(id)

    def get_compact_id(self):
        try:
            return "%s:%s" % (self.atributes["testset"], self.attributes["id"])
        except:
            sys.stderr.write("Could not add set id into compact sentence id")
            return self.attributes["id"]
    
    def get_source(self):
        return self.src
    
    def set_source(self,src):
        self.src = src
    
    def get_translations(self):
        return self.tgt
    
    def set_translations(self, tgt):
        self.tgt = tgt
    
    def get_reference(self):
        return self.ref
    
    def set_reference(self,ref):
        self.ref = ref
    
    def get_nested_attributes(self):
        """
        function that gathers all the features of the nested sentences 
        to the parallel sentence object, by prefixing their names accordingly
        """
        
        new_attributes = deepcopy (self.attributes)
        new_attributes.update( self.__prefix__(self.src.get_attributes(), "src") )
        i=0
        for tgtitem in self.tgt:
            i += 1
            prefixeditems = self.__prefix__( tgtitem.get_attributes(), "tgt-%d" % i )
            #prefixeditems = self.__prefix__( tgtitem.get_attributes(), tgtitem.get_attributes()["system"] )
            new_attributes.update( prefixeditems )

        try:
            new_attributes.update( self.__prefix__( self.ref.get_attributes(), "ref" ) )
        except:
            pass
        return new_attributes


    def recover_attributes(self):
        """
        Moves the attributes back to the nested sentences
            
        """
        
        for attribute_name in self.attributes.keys():
            attribute_value =  self.attributes[attribute_name] 
            if (attribute_name.find('_') > 0) :

                src_attribute = re.match("src_(.*)", attribute_name)
                if src_attribute:
                    self.src.add_attribute(src_attribute.group(1), attribute_value)
                    del self.attributes[attribute_name]
                
                ref_attribute = re.match("ref_(.*)", attribute_name)
                if ref_attribute:
                    self.src.add_attribute(ref_attribute.group(1), attribute_value)
                    del self.attributes[attribute_name]
                
                tgt_attribute = re.match("tgt-([0-9]*)_(.*)", attribute_name)
                if tgt_attribute:
                    index = int(tgt_attribute.group(1)) - 1
                    new_attribute_name = tgt_attribute.group(2)
                    self.tgt[index].add_attribute(new_attribute_name, attribute_value)
                    del self.attributes[attribute_name]

    
    def serialize(self):
        list = []
        list.append(self.src)
        list.extend(self.tgt)
        return list
        
        
    def __prefix__(self, listitems, prefix):
        newlistitems = {}
        for item_key in listitems.keys():
            new_item_key = "_".join([prefix, item_key]) 
            newlistitems[new_item_key] = listitems[item_key]
        return newlistitems
    

    def merge_parallelsentence(self, ps, attribute_replacements = {}):
        """
        Augment the parallelsentence with another parallesentence. 
        Merges attributes of source, target and reference sentences and adds target sentences whose system doesn't exist. 
        attributes of target sentences that have a common system.
        @param ps: Object of ParallelSentence() with one source sentence and more target sentences
        @type ps: sentence.parallelsentence.ParallelSentence 
        """
        
        #merge attributes on the ParallelSentence level and do the replacements
        incoming_attributes = ps.get_attributes()
        for incoming_attribute in incoming_attributes:
            if incoming_attribute in attribute_replacements:
                new_key = attribute_replacements[incoming_attribute]
                new_value = incoming_attributes[incoming_attribute]
                incoming_attributes[new_key] = new_value
                del(incoming_attributes[incoming_attribute])            
        
        self.attributes.update(incoming_attributes)
        
        #merge source sentence
        self.src.merge_simplesentence(ps.get_source(), attribute_replacements)
        
        #merge reference translation
        try:
            self.ref.merge_simplesentence(ps.get_reference(), attribute_replacements)
        except:
            pass
        
        #loop over the contained target sentences. Merge those with same system attribute and append those missing
        for tgtPS in ps.get_translations():
            system = tgtPS.get_attribute("system")
            merged = False
            for i in range(len(self.tgt)):
                if self.tgt[i].attributes["system"] == system:
                    self.tgt[i].merge_simplesentence(tgtPS, attribute_replacements)
                    merged = True
            if not merged:
                #print tgtPS.get_attributes(), "not merged - unknown system!"
                print "Target sentence was missing. Adding..."
                self.tgt.append(tgtPS)


    def get_pairwise_parallelsentence_set(self, directed = False):
        """
        Create a set of all available parallel sentence pairs (in tgt) from one ParallelSentence object.
        @param ps: Object of ParallelSetnece() with one source sentence and more target sentences
        @type ps: sentence.parallelsentence.ParallelSentence
        @return p: set of parallel sentence pairs from one PS object
        @type p: a list of PairwiseParallelSentence() objects
        """
        from pairwiseparallelsentence import PairwiseParallelSentence
        from pairwiseparallelsentenceset import PairwiseParallelSentenceSet
        
        systems = []
        targets = []
        systems_list = []
        targets_list = []
        for targetA in self.get_translations():
            system_nameA = targetA.get_attribute('system')
            for system_nameB in systems_list:
                systems.append((system_nameA, system_nameB))
                if not directed:
                    systems.append((system_nameB, system_nameA))
            for targetB in targets_list:
                targets.append((targetA, targetB))
                if not directed:
                    targets.append((targetB, targetA))
            systems_list.append(system_nameA)
            targets_list.append(targetA)

        pps_list = [PairwiseParallelSentence(self.get_source(), targets[i], systems[i], self.get_reference()) \
                        for i in range(len(systems))]
        p = PairwiseParallelSentenceSet(pps_list)
        return p
