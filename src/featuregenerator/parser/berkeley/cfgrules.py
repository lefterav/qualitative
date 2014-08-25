'''
Contains the feature generator and the necessary functions for extracting CFG rules from bracketed Berkeley parses

Created on Jul 13, 2014

@author: Eleftherios Avramidis
'''
import logging

#from featuregenerator.ibm1 import AlignmentFeatureGenerator
#from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator 
#from numpy import average
#from featuregenerator.featuregenerator import FeatureGenerator

from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator 
from numpy import average
from featuregenerator.featuregenerator import FeatureGenerator

from nltk.align import AlignedSent
import re
import sys

def xml_normalize(string):
        string = string.replace("$,", "COMMA") #german grammar
        string = string.replace(",", "COMMA")
        string = string.replace("$.", "DOT") #german grammar        
        string = string.replace(".", "DOT")
        string = string.replace(";", "DOT")
        string = string.replace("$", "DLR")
        string = string.replace("*", "_")
        string = string.replace(":", "PUNCT")
        string = string.replace('"', "QUOT")
        string = string.replace("'", "QUOT")
        string = re.sub("[^A-Za-z0-9_]", "_", string)
        return string


class Rule:
    def __init__(self):
        self.lhs = None
        self.rhs = []
        self.depth = 0
        self.length = 0
        self.leaves = []
        self.indices = set()
    
    def __str__(self): 
        string = "{}_{}".format(self.lhs, "-".join(self.rhs))
        return xml_normalize(string)        


def get_cfg_rules(string, terminals=False):
    '''
    Parse the bracketed format from a Berkley PCFG parse 
    and extract the CFG rules included
    @param string: the parse in a bracketed format
    @type string: str
    @return: the CFG rules 
    @rtype: str
    '''
    
    #a stack stores the rules met upper on the tree and may
    #have remained incomplete
    stack = []
    
    #always track current depth and number of leaves
    depth = 0   
    index = 0
    
    #the label gathers the characters of the labels as they appear
    #one by one
    label = []
    
    #as we go, we keep track of the previous (unfinished) rule
    previousrule = Rule()
    #root = previousrule #not needed for now
    
    #the rules that are ready get in this list
    rules = []
    
    #get characters one by one (to catch-up with brackets)
    prevchar = None
    for char in list(string):
        logging.debug(char)
        
        #opening bracket initiates a rule (remains open)
        if char=="(":
            depth += 1
            nextrule = Rule()
            label = []
            
        #space indicates the label is finished and can be 
        #attached to the previous rule as a child (RHS)
        #and the new rule as a head (LHS)
        elif char==" " and prevchar != ")": #not after a closing bracket
            labelstr = "".join(label)
            previousrule.rhs.append(labelstr)
            nextrule.lhs = labelstr
            nextrule.depth = depth
            logging.debug("Next rule: {}".format(nextrule))
            
            #previous rule from upper nodes goes to the stack
            stack.append(previousrule)
            logging.debug("Stacking previous rule: {}".format(previousrule))
            #and next rule (still open) becomes current rule 
            #waiting for children
            previousrule = nextrule
            label = []
            
        #closing bracket indicates that a rule is closed/ready
        #and can be delivered
        elif char==")" and stack:
            depth -= 1
            current_length = 0

            if not previousrule.rhs:
                previousrule.leaves.append("".join(label))
                previousrule.indices.add(index)
                previousrule.length += 1
                index+=1
            current_length = previousrule.length
            current_leaves = previousrule.leaves
            current_indices = previousrule.indices
            #deliver rule but maybe exclude leaves
            if previousrule.rhs or terminals:
                rules.append(previousrule)
                
            logging.debug("Previous rule getting stored: {}".format(previousrule))
            
            #we need to pop the rule from the node above, because
            #it may get more RHS in the next loop
            previousrule = stack.pop()
            previousrule.length += current_length
            previousrule.leaves.extend(current_leaves)
            previousrule.indices.update(current_indices)
            logging.debug("Popping previousrule: {}".format(previousrule))
            label = []
        #get characters for the label
        else:
            label.append(char)
        logging.debug("---")
        
        #remember the previous character, to consider space after 
        #closing bracket
        prevchar = char
    return rules    


class CfgRulesExtractor(FeatureGenerator):
    '''
    Handle the extraction of features out of CFG rules 
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def get_features_simplesentence(self, simplesentence, parallelsentence):
        '''
        Count the CFG rules appearing in the parse
        '''
        try:
            parsestring = simplesentence.get_attribute("berkeley-tree")
        except:
            print "error reading berkeley tree"
            return {}
        cfg_rules = get_cfg_rules(parsestring)
        atts = {}
        
        ruledepth = {}
        labeldepth = {}
        labelleaves = {}
        fulldepth = 0
        
        for rule in cfg_rules:
            ruledepth[rule] = ruledepth.setdefault(rule, []).append(rule.depth)
            labeldepth.setdefault(rule.lhs, []).append(rule.depth)
            labelleaves.setdefault(rule.lhs, []).append(rule.length) 
            if rule.depth > fulldepth:
                fulldepth = rule.depth
            
        for label, depthvector in labeldepth.iteritems():
            try:
                atts["parse_{}_depth_max".format(label)] = max(depthvector)
                atts["parse_{}_height_max".format(label)] = fulldepth - max(depthvector)
                atts["parse_{}_depth_avg".format(label)] = average(depthvector)
                atts["parse_{}_height_avg".format(label)] = fulldepth - average(depthvector)
            except:
                atts["parse_{}_depth_max".format(label)] = 0
                atts["parse_{}_height_max".format(label)] = 0
                atts["parse_{}_depth_avg".format(label)] = 0
                atts["parse_{}_height_avg".format(label)] = 0
            
        for label, leavevector in labelleaves.iteritems():
            try:
                atts["parse_{}_leaves_max".format(label)] = max(leavevector)
                atts["parse_{}_leaves_avg".format(label)] = average(leavevector)
            except:
                atts["parse_{}_leaves_max".format(label)] = 0
                atts["parse_{}_leaves_avg".format(label)] = 0
        
        for rule in cfg_rules:
            atts["cfg_{}".format(rule)] =  atts.setdefault("cfg_{}".format(rule), 0) + 1
            try:
                atts["cfg_{}_depth_max".format(rule)] = max(ruledepth.setdefault(rule, []))
                atts["cfg_{}_depth_avg".format(rule)] = average(ruledepth.setdefault(rule, []))
                atts["cfg_{}_height_max".format(rule)] = fulldepth - max(ruledepth.setdefault(rule, []))
                atts["cfg_{}_height_avg".format(rule)] = fulldepth - average(ruledepth.setdefault(rule, []))
                
            except:
                atts["cfg_{}_depth_max".format(rule)] = 0
                atts["cfg_{}_depth_avg".format(rule)] = 0
                atts["cfg_{}_height_max".format(rule)] = fulldepth
                atts["cfg_{}_height_avg".format(rule)] = fulldepth
                            
            atts["cfg_fulldepth"] = fulldepth
            
        return atts    
        
class CfgAlignmentFeatureGenerator(FeatureGenerator):
    def __init__(self):
        #TODO: self.alignment = AlignmentFeatureGenerator(giza_filename)
        pass
        
    def get_features_tgt(self, targetsentence, parallelsentence):
        source_line = parallelsentence.get_source().get_string()
        target_line = targetsentence.get_string()
        alignment_string = targetsentence.get_attribute("imb1-alignment-joined")
        sourceparse = parallelsentence.get_source().get_attribute("berkeley-tree")
        targetparse = targetsentence.get_attribute("berkeley-tree")
        
        return self.process_string(source_line, target_line, alignment_string, sourceparse, targetparse)
   
    def _get_unaligned_target_indices(self, target_line, alignment_string):
        alignedindices = set()
        for _, targetindex in [t.split("-") for t in alignment_string.split()]:
             alignedindices.add(int(targetindex))
        allindices = set(range(len(target_line.split())))
        unaligned = allindices - alignedindices
        logging.debug("Unaligned indices on target {}".format(",".join([str(i) for i in unaligned ])))
        return unaligned
    
    def process_string(self, source_line, target_line, alignment_string, sourceparse, targetparse):
        print alignment_string 
        aligned_sentence = AlignedSent(source_line.split(),
                                target_line.split(),
                                alignment_string)
        sourcerules = get_cfg_rules(sourceparse, True)
        targetrules = get_cfg_rules(targetparse, True)
        
        rule_alignments = []
        
        for sourcerule in sourcerules:
            source_label = sourcerule.lhs
            logging.debug("Alignment string: {}".format(alignment_string))
            logging.debug("Source indices: {}".format(sourcerule.indices)) 
            try:
                target_indices = aligned_sentence.alignment.range(list(sourcerule.indices))
            except IndexError:
                target_indices = []            
#            logging.warning("AlignedSent from NLTK caused an exception for sourcerule {}".format(sourcerule))

            
            for unaligned_index in self._get_unaligned_target_indices(target_line, alignment_string):
                if target_indices and unaligned_index > min(target_indices) and unaligned_index < max(target_indices):
                    target_indices.append(unaligned_index)
            logging.debug("label: {} -> {}".format(source_label, ",".join([str(i) for i in sorted(target_indices)])))
            matched_labels = self._match_targetlabels(targetrules, target_indices)
            rule_alignments.append((source_label, sourcerule.depth, matched_labels))
          
        atts = {}
        for source_label, depth, matched_labels in rule_alignments:
            if matched_labels:
                rule_alignment_string = "{}_{}".format(source_label, "-".join(matched_labels))
            else:
                rule_alignment_string = "{}_{}".format(source_label, "-none")
            key = xml_normalize("cfgal_{}".format(rule_alignment_string))
            atts[key] = min([atts.setdefault(key, 100), depth]) 
        return atts

    
    def _match_targetlabels(self, targetrules, target_indices):
        candidate_labels = []
        for targetrule in targetrules:
            logging.debug("t-label: {} -> {}".format(targetrule, ",".join([str(i) for i in targetrule.indices])))
            if targetrule.indices.issubset(target_indices):
                candidate_labels.append((targetrule.depth, targetrule.lhs))
        if not candidate_labels:
            return []    
        min_depth , _ = min(candidate_labels)
        matched_labels = [label for length, label in candidate_labels if length==min_depth]
        logging.debug("chosen labels: {}".format(matched_labels))
        return matched_labels

from dataprocessor.ce.cejcml import CEJcmlReader
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from featuregenerator.ibm1 import AlignmentFeatureGenerator
from dataprocessor.sax import saxjcml

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
 
    cfgalignmentprocessor = CfgAlignmentFeatureGenerator()
    srcalignmentfile = "/share/taraxu/systems/r2/de-en/moses/model/lex.2.e2f"
    tgtalignmentfile = "/share/taraxu/systems/r2/de-en/moses/model/lex.2.f2e"

    aligner = AlignmentFeatureGenerator(srcalignmentfile, tgtalignmentfile)
#    reader = CEJcmlReader(sys.argv[1])
#    for parallelsentence in reader.get_parallelsentences():
    

   # sourcestring = SimpleSentence("Keine befreiende Novelle fuer Tymoshenko durch das Parlament", 
#                                  {'berkeley-tree':"(PSEUDO (NP (PIAT Keine) (ADJA befreiende) (NN Novelle)) (NP (ADJA fuer) (NN Tymoshenko) (PP (APPR durch) (ART das) (NN Parlament)))) )"}
#                                  )
   # targetstring = SimpleSentence("No releasing novella for Tymoshenko by the parliament",
#                                  {'berkeley-tree': "(S (NP (DT No) (VBG releasing)) (VP (VBD novella) (PP (IN for) (NP (NNP Tymoshenko))) (PP (IN by) (NP (DT the) (NN parliament))))) )"}
#                                  )
   # parallelsentence = ParallelSentence(sourcestring, [targetstring], None, {'langsrc' : "de", 'langtgt' : "en"})
        #parallelsentence = aligner.add_features_parallelsentence(parallelsentence)
        #parallelsentence3 = cfgalignmentprocessor.add_features_parallelsentence(parallelsentence2)
        #print parallelsentence
    input_file = sys.argv[1]
    output_file = input_file + "out.jcml"
    analyzers = [aligner, cfgalignmentprocessor ]
    saxjcml.run_features_generator(input_file, output_file, analyzers)
#    saxjcml.run_features_generator(input_file, output_file, analyzers)
    
