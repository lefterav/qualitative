"""
Provides the class which contains the information and meta-data of a parallel sentence
@author: Eleftherios Avramidis
"""

from collections import OrderedDict
from copy import deepcopy
import re
import sys
import logging
import logging as log
from ranking import Ranking
import itertools
import numpy as np

def _prefix(prefix, names):
    return [prefix.format(name) for name in names]    

def _deprefix(prefix, names):
    pattern = re.compile("{}_(.*)".format(prefix))
    deprefixed = []
    for attname in names:
        try:
            name = re.findall(pattern, attname)[0]
            deprefixed.append(name)
        except:
            pass
    return deprefixed

def _noprefix(prefixes, names):
    notprefixed = []
    for name in names:
        if not True in [name.startswith("{}".format(prefix)) for prefix in prefixes]:
            notprefixed.append(name)
    return notprefixed

class AttributeSet:
    def __init__(self, 
                 parallel_attribute_names=[], 
                 source_attribute_names=[],
                 target_attribute_names=[],
                 ref_attribute_names=[]):
        self.parallel_attribute_names = parallel_attribute_names
        self.source_attribute_names = source_attribute_names
        self.target_attribute_names = target_attribute_names
        self.ref_attribute_names = ref_attribute_names

    def get_names_pairwise(self):
        all_attribute_names = []
        all_attribute_names.extend(self.parallel_attribute_names)
        #attribute names for source and target pairs need to be prefixed 
        all_attribute_names.extend(_prefix("src_{}", self.source_attribute_names))
        all_attribute_names.extend(_prefix("tgt-1_{}", self.target_attribute_names))
        all_attribute_names.extend(_prefix("tgt-2_{}", self.target_attribute_names))
        return all_attribute_names
    
    def set_names_from_pairwise(self, pairwise_names=[]):
        self.source_attribute_names = _deprefix("src", pairwise_names)
        self.target_attribute_names = _deprefix("tgt-1", pairwise_names)
        self.ref_attribute_names = _deprefix("ref", pairwise_names)
        self.parallel_attribute_names = _noprefix(["src", "tgt", "ref"], pairwise_names)

    def __str__(self):
        return str([self.parallel_attribute_names, self.source_attribute_names, self.target_attribute_names])
        
            

class ParallelSentence(object):
    """
    A parallel sentence, that contains a source sentence, 
    a number of target sentences, a reference and some attributes
    @ivar src: the source sentence
    @type src: SimpleSentence
    @ivar tgt: a list of target sentences / translations
    @type tgt: [SimpleSentence, ...]
    @ivar ref: a reference translation
    @type ref: SimpleSentence
    """
    

    def __init__(self, source, translations, reference = None, attributes = {}, rank_name = "rank", **kwargs):
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
        @keyword sort_translations: Whether translations should be sorted based on the system name
        @type sort_translations: boolean 
        """
        self.src = source 
        self.tgt = translations
        if type(self.tgt) is not list:
            raise TypeError("ParalleSentence target sentences should be a list")
        self.ref = reference
        self.attributes = deepcopy (attributes)
        self.rank_name = rank_name
        if kwargs.setdefault("sort_translations", False):
            self.tgt = sorted(translations, key=lambda t: t.get_attribute("system"))
                
    
        try:
            self.attributes["langsrc"] = kwargs.setdefault("langsrc", self.attributes["langsrc"])
            self.attributes["langtgt"] = kwargs.setdefault("langtgt", self.attributes["langtgt"])
        except KeyError:
            sys.exit('Source or target language not specified in parallelsentence: [{}]'.format(self.__str__()))
    
    def __str__(self):
        return ", ".join([s.__str__() for s in self.serialize()])
        
    def __lt__(self, other):
        return self.get_compact_id() < other.get_compact_id()
        
    def __gt__(self, other):
        return self.get_compact_id() > other.get_compact_id()
    
    def __eq__(self, other):
        
            print self.src == other.src
            print self.tgt == other.tgt 
            print self.attributes == other.attributes  
             
            
            return ( 
            self.src == other.src and 
            self.tgt == other.tgt and 
            self.ref == other.ref and
            self.attributes == other.attributes)
        
        
    
    def get_rank(self):
        """
        provide the rank value of the parallel sentence
        return: the rank value 
        rtype: string
        """
        return self.attributes[self.rank_name]
    
    def get_ranking(self):
        """
        returns a ranking list, containing the ranks of the included
        target translations
        @return: the ranking list
        @rtype: Ranking
        """
        return Ranking([s.get_rank() for s in self.tgt])
            
    def get_attributes(self):
        """
        provide all attributes
        @return: the parallel sentence attributes dictionary
        @rtype: dict([(string,string), ...])
        """
        return self.attributes
    
    def get_attribute_names (self):
        """
        provide all attribute names
        @return: a set with the names of the attributes
        @rtype: set([string, ...])
        """
        return self.attributes.keys()
    
    def get_attribute(self, name):
        """
        provide the value of a particular attribute
        @return: the value of the attribute with the specified name
        @rtype: string
        """
        return self.attributes[name]            
    
    def get_target_attribute_values(self, attribute_name, sub=None):
#       print [t.attributes for t in self.tgt]
        attribute_values = [target.get_attribute(attribute_name, sub) for target in self.tgt]        
        return attribute_values

    def get_filtered_target_attribute_values(self, attribute_name, filter_attribute_name, filter_attribute_value):
        attribute_values = [target.get_attribute(attribute_name) for target in self.tgt if target.get_attribute(filter_attribute_name) != filter_attribute_value]        
        return attribute_values

    def add_attributes(self, attributes):
        self.attributes.update( attributes )
    
    def set_langsrc(self, langsrc):
        self.attributes["langsrc"] = langsrc

    def set_langtgt(self, langtgt):
        self.attributes["langtgt"] = langtgt
        
    def get_langsrc(self):
        return self.attributes["langsrc"]

    def get_langtgt(self):
        return self.attributes["langtgt"]
    
    def get_langpair(self):
        return "{}-{}".format(self.attributes["langsrc"],
                              self.attributes["langtgt"])
        
    def set_id (self, id):
        self.attributes["id"] = str(id)
        
    def get_id (self):
        return self.attributes["id"]

    def get_compact_id(self):
        try:
            return "%s:%s" % (self.attributes["testset"], self.attributes["id"])
        except:
#            sys.stderr.write("Warning: Could not add set id into compact sentence id %s\n" %  self.attributes["id"])
            return self.attributes["id"]
        
    def get_tuple_id(self):
        try:
            return (self.attributes["testset"], self.attributes["id"])
        except:
#            sys.stderr.write("Warning: Could not add set id into compact sentence id %s\n" %  self.attributes["id"])
            return (self.attributes["id"])
    
    def get_compact_judgment_id(self):
        try:
            return "%s:%s" % (self.attributes["testset"], self.attributes["judgement_id"])
        except:
#            sys.stderr.write("Warning: Could not add set id into compact sentence id %s\n" %  self.attributes["id"])
            return self.attributes["judgement_id"]        
               
    def get_judgment_id(self):
        return self.attributes["judgement_id"]
    
    def has_judgment_id(self):
        return self.attributes.has_key("judgement_id")
    
    def add_judgment_id(self, value):
        self.attributes["judgement_id"] = str(value)
    
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
    
    def get_nested_attribute_names(self):
        attribute_names = []
        attribute_names.extend(self.attributes.keys())
        
        source_attribute_names = [attribute_names.append("src_{}".format(att)) for att in self.src.get_attributes()]
        attribute_names.extend(source_attribute_names)
        
        i=0
        for tgtitem in self.tgt:
            i += 1
            target_attribute_names = [attribute_names.append("tgt-{}_{}".format(i,att)) for att in tgtitem.get_attributes()]
            attribute_names.extend(target_attribute_names)
        return attribute_names

    def get_nested_attributes(self):
        """
        function that gathers all the features of the nested sentences 
        to the parallel sentence object, by prefixing their names accordingly
        """
        
        new_attributes = deepcopy (self.attributes)
        new_attributes.update( self._prefix(self.src.get_attributes(), "src") )
        i=0
        for tgtitem in self.tgt:
            i += 1
            prefixeditems = self._prefix( tgtitem.get_attributes(), "tgt-%d" % i )
            #prefixeditems = self._prefix( tgtitem.get_attributes(), tgtitem.get_attributes()["system"] )
            new_attributes.update( prefixeditems )

        try:
            new_attributes.update( self._prefix( self.ref.get_attributes(), "ref" ) )
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
        
        
    def _prefix(self, listitems, prefix):
        newlistitems = OrderedDict()
        for item_key in listitems.keys():
            new_item_key = "_".join([prefix, item_key]) 
            newlistitems[new_item_key] = listitems[item_key]
        return newlistitems
    

    def merge_parallelsentence(self, ps, attribute_replacements = {}, **kwargs):
        """
        Augment the parallelsentence with another parallesentence. 
        Merges attributes of source, target and reference sentences and adds target sentences whose system doesn't exist. 
        attributes of target sentences that have a common system.
        @param ps: Object of ParallelSentence() with one source sentence and more target sentences
        @type ps: sentence.parallelsentence.ParallelSentence
        @param add_missing: If translation outputs are missing from the first file but exist in the second, add them (default: True)
        @type add_missing: boolean  
        """
        
        add_missing = kwargs.setdefault("add_missing", True)
        
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
            if not merged and add_missing:
                #print tgtPS.get_attributes(), "not merged - unknown system!"
                sys.stderr.write("Warning: Target sentence was missing. Adding...\n")
                self.tgt.append(tgtPS)

    def get_pairwise_parallelsentences(self, 
                                       bidirectional_pairs=True,
                                       class_name=None,
                                       ties=True):
        
        from pairwiseparallelsentence import PairwiseParallelSentence
        
        #parallel_attribute_values = [self.attributes[name] for name in attribute_set.parallel_attribute_names]
        #source_attribute_values = [self.src.attributes[name] for name in attribute_set.source_attribute_names]

        if bidirectional_pairs:
            iterator = itertools.permutations(self.tgt, 2)
        else:
            iterator = itertools.combinations(self.tgt, 2)
            #logging.info("{}".format([(s1.get_attribute("system"), s2.get_attribute("system")) for s1,s2 in iterator ]))
        
        for target1, target2 in iterator:
            targets = (target1, target2)
            systems = (target1.get_attribute("system"), target2.get_attribute("system"))
            pairwise_parallelsentence = PairwiseParallelSentence(self.src, 
                                                                 translations=targets, 
                                                                 systems=systems, 
                                                                 attributes=self.attributes,
                                                                 reference=self.ref,
                                                                 rank_name=class_name)
            if class_name:
                class_value = self._get_class_pairwise(target1, target2, class_name, ties=False)
                if class_value == 0 and not ties:
                    logging.info("{}, skipped tie".format(systems))                               
                elif class_value!= None:
                    rank_attname = pairwise_parallelsentence.rank_name
                    pairwise_parallelsentence.attributes[rank_attname] = class_value
                    yield pairwise_parallelsentence 
                else: 
                    yield pairwise_parallelsentence 
        

    def get_pairwise_parallelsentences_old(self, replacement = True, **kwargs):
        """
        Create a set of all available parallel sentence pairs (in tgt) from one ParallelSentence object.
        @param ps: Object of ParallelSetnece() with one source sentence and more target sentences
        @type ps: sentence.parallelsentence.ParallelSentence

        kwargs:
        @param replacement: If enabled, creates pairs with all possible combinations with replacement
        @type replacement: boolean
        @param include_references: Include references as system translations from system "_ref" and lowest rank
        @type include_references: boolean
        @param filter_unassigned: If enabled, it filters out pairs with rank = "-1", which means no value was assigned
        It should not be turned on for test-sets 
        @type filter_unassigned: boolean
        @param restrict_ranks: Filter pairs to keep only for the ones that include the given ranks. Don't filter if list empty. Before
        using this, make sure that the ranks are normalized        
        @type restrict_ranks: [int, ...] 
        
        @return p: set of parallel sentence pairs from one PS object
        @type p: a list of PairwiseParallelSentence() objects
        
        """
        from pairwiseparallelsentence import PairwiseParallelSentence
        
        replacement = kwargs.setdefault("replacement", replacement)
        include_references = kwargs.setdefault("include_references", False)
        restrict_ranks = kwargs.setdefault("restrict_ranks", [])
        invert_ranks = kwargs.setdefault("invert_ranks", [])
        rank_name = kwargs.setdefault("rank_name", self.rank_name)
        rankless = kwargs.setdefault("rankless", False)
        ties = kwargs.setdefault("ties", True)
        
        systems = []
        targets = []
        systems_list = []
        targets_list = []
        if not ties:
            self.remove_ties()
        
        translations = self.get_translations()
        if kwargs.setdefault('filter_unassigned', False):
            translations = [t for t in self.get_translations() if t.get_attribute(self.rank_name) != "-1"]    
        #this is used in case we want to include references in the pairwising
        #references are added as translations by system named _ref
        #only single references supported at the moment
        if include_references:
            if "_ref" not in self.get_target_attribute_values("system"):    
                reference = self.get_reference()
                reference.add_attribute("system", "_ref") 
                if not rankless: 
                    #get a rank value lower than all the existing ones and assign it to references
                    min_rank = min([float(t.get_attribute(self.rank_name)) for t in translations]) - 1 
                    reference.add_attribute(self.rank_name, str(int(min_rank)))
                    translations.append(reference)
                    
        #@todo: rewrite this function in more efficient way
        for targetA in translations:
            system_nameA = targetA.get_attribute('system')
            for system_nameB in systems_list:
                systems.append((system_nameA, system_nameB))
                if replacement:
                    systems.append((system_nameB, system_nameA))
            for targetB in targets_list:
                targets.append((targetA, targetB))
                if replacement:
                    targets.append((targetB, targetA))
            systems_list.append(system_nameA)
            targets_list.append(targetA)


        for i in range(len(systems)):
            pairwise_parallel_sentence = PairwiseParallelSentence(self.get_source(), 
                                             targets[i], 
                                             systems[i], 
                                             self.ref, 
                                             self.attributes, 
                                             rank_name, 
                                             invert_ranks = invert_ranks,
                                             rankless = rankless
                                             ) 
            yield pairwise_parallel_sentence
    

    def import_indexed_parallelsentence(self, parallelsentence, target_attribute_names, keep_attributes_general=[], keep_attributes_source=[], keep_attributes_target=[]):
        """
        """
        targets = self.get_translations()
        
        incoming_targets = parallelsentence.get_translations()
        incoming_translations = dict([(tgt.get_attribute("system"), tgt) for tgt in incoming_targets])
        #print parallelsentence.get_attribute("judgement_id")
        #print self.get_attribute("judgement_id")
        
        #print [t.get_attribute("system") for t in incoming_targets]
        #print [t.get_attribute("system") for t in targets]
       
        #print 
 
        new_targets = []
        self.src.keep_only_attributes(keep_attributes_source)

        for target in targets:
            system_id = target.get_attribute("system")
            matched_incoming = incoming_translations[system_id]
            for attribute_name in target_attribute_names:
                value = matched_incoming.get_attribute(attribute_name)
                target.keep_only_attributes(keep_attributes_target)
                target.add_attribute(attribute_name, value)
            new_targets.append(target)
                
        self.tgt = new_targets
        
        for name in self.attributes.keys():
            if name not in keep_attributes_general:
                del(self.attributes[name])
        self.ref = None

    def import_missing_parallelsentence(self, target_attribute_names, keep_attributes_general=[], keep_attributes_source=[], keep_attributes_target=[]):
        targets = self.get_translations()
        
        
        

        new_targets = []
        self.src.keep_only_attributes(keep_attributes_source)

        for target in targets:
            system_id = target.get_attribute("system")
            for attribute_name in target_attribute_names:
                #only for rank
                value = '1'
                target.keep_only_attributes(keep_attributes_target)
                target.add_attribute(attribute_name, value)
            new_targets.append(target)
                
        self.tgt = new_targets
        
        for name in self.attributes.keys():
            if name not in keep_attributes_general:
                del(self.attributes[name])
        self.ref = None
        

    def remove_ties(self):
        """
        Function that modifies the current parallel sentence by removing the target translations that create ties. 
        Only first translation for each rank is kept
        """
        translation_per_rank = [(tgt.get_rank(), tgt) for tgt in self.tgt]
        prev_rank = None
        remaining_translations = []
        for system, translation in sorted(translation_per_rank):
            rank = int(translation.get_rank())
            if prev_rank != rank:
                remaining_translations.append(translation)
                prev_rank = rank 
            else:
                logging.debug("Filtered translation from {} because it tied".format(system))   
        self.tgt = remaining_translations



    def get_vectors(self, attribute_set, bidirectional_pairs=True, ties=False, class_name=None, default_value='', replace_infinite=False, replace_nan=False):
        """
        Return a feature vector in an efficient way, where only specified attributes are included
        @param attribute_set: a definition of the attribute that need to be included
        @type attribute_set: L{AttributeSet}
        @return: one vector for each pairwise comparison of target sentences
        @rtype: C{iterator} of C{lists}
        """
       
        yielded = 0
        parallel_attribute_values = self.get_vector(attribute_set.parallel_attribute_names, default_value, replace_infinite, replace_nan)
        source_attribute_values = self.src.get_vector(attribute_set.source_attribute_names, default_value, replace_infinite, replace_nan)

        if len(self.tgt)==0:
            log.warning("Parallelsentence has got only one target sentence, so cannot produce pairs")

        if bidirectional_pairs:
            iterator = itertools.permutations(self.tgt, 2)
        else:
            iterator = itertools.combinations(self.tgt, 2)
        
        for target1, target2 in iterator:
            target1_attribute_values = target1.get_vector(attribute_set.target_attribute_names, default_value, replace_infinite, replace_nan)
            target2_attribute_values = target2.get_vector(attribute_set.target_attribute_names, default_value, replace_infinite, replace_nan)
           
            log.debug("Parallelsentence received vector 1: {} ".format(target1_attribute_values))
            log.debug("Parallelsentence received vector 2: {} ".format(target2_attribute_values))

            vector = []
            vector.extend(parallel_attribute_values)
            vector.extend(source_attribute_values)
            vector.extend(target1_attribute_values)
            vector.extend(target2_attribute_values)
            
            log.debug("Combined vector: {}".format(vector))

            yielded+=1

            if class_name:
                class_value = self._get_class_pairwise(target1, target2, class_name, ties)
                if class_value!=None:
                    yield vector, class_value
                else:
                    log.debug("Target sentence pair did not provide class value")
            else:  
                yield vector, None
        if yielded==0:
            log.warning("Parallelsentence did not produce any pairs")

    def get_vector(self, attribute_names, default_value='', replace_infinite=False, replace_nan=False):
        vector = []
        for name in attribute_names:
            try:
                attvalue = float(self.attributes[name])
                if replace_infinite:
                    attvalue = float(str(attvalue).replace("inf", "500"))
                if replace_nan:
                    attvalue = float(str(attvalue).replace("nan", "0"))
                vector.append(attvalue)
            except KeyError:
                vector.append(default_value)
        return vector
    
            
    def _get_class_pairwise(self, target1, target2, class_name, ties):
        try:
            if target1[class_name] > target2[class_name]:
                class_value = 1
            elif target1[class_name] < target2[class_name]:
                class_value = -1
            elif ties:
                class_value = 0
            else:
                class_value = None
            return class_value
        except KeyError:
            return None
        
                
        


        
    
    
    
