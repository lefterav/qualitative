'''
Contains the feature generator and the necessary functions for extracting CFG rules from bracketed Berkeley parses

Created on Jul 13, 2014

@author: Eleftherios Avramidis
'''
import logging
from numpy import average
from featuregenerator.featuregenerator import FeatureGenerator

class Rule:
    def __init__(self):
        self.lhs = None
        self.rhs = []
        self.depth = 0
        
    def __str__(self):
        string = "{}_{}".format(self.lhs, "-".join(self.rhs))
        string = string.replace("$,", "COMMA") #german grammar
        string = string.replace(",", "COMMA")
        string = string.replace("$.", "DOT") #german grammar        
        string = string.replace(".", "DOT")
        string = string.replace(";", "DOT")        
        string = string.replace("$", "DLR")
        string = string.replace("*", "_")
        string = string.replace(":", "PUNCT")        
        return string        

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
    
    #always track current depth
    depth = 0    
    
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
        
            #deliver rule but maybe exclude leaves
            if previousrule.rhs or terminals:
                rules.append(previousrule)
                
            logging.debug("Previous rule getting stored: {}".format(previousrule))
            
            #we need to pop the rule from the node above, because
            #it may get more RHS in the next loop
            previousrule = stack.pop()
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
        fulldepth = 0
        
        for rule in cfg_rules:
            ruledepth[rule] = ruledepth.setdefault(rule, []).append(rule.depth)
            labeldepth[rule.lhs] = labeldepth.setdefault(rule, []).append(rule.depth)
            if rule.depth > fulldepth:
                fulldepth = rule.depth
            
        for label, depthvector in labeldepth.iteritems():
            try:
                atts["parse_{}_depth_max".format(label)] = max(depthvector) 
                atts["parse_{}_height_max".format(label)] = fulldepth - max(depthvector)
                atts["parse_{}_depth_avg".format(label)] = average(depthvector)
                atts["parse_{}_height_avg".format(label)] = fulldepth - average(depthvector)
            except:
                pass
            
        
        for rule in cfg_rules:
            atts["cfg_{}".format(rule)] =  atts.setdefault("cfg_{}".format(rule), 0) + 1
            try:
                atts["cfg_{}_depth_max".format(rule)] = max(ruledepth.setdefault(rule, []))
                atts["cfg_{}_depth_avg".format(rule)] = average(ruledepth.setdefault(rule, []))
                atts["cfg_{}_height_max".format(rule)] = fulldepth - max(ruledepth.setdefault(rule, []))
                atts["cfg_{}_height_avg".format(rule)] = fulldepth - average(ruledepth.setdefault(rule, []))
                
            except ValueError:
                atts["cfg_{}_depth_max".format(rule)] = 0
                atts["cfg_{}_depth_avg".format(rule)] = 0
                atts["cfg_{}_height_max".format(rule)] = fulldepth
                atts["cfg_{}_height_avg".format(rule)] = fulldepth
                            
            atts["cfg_fulldepth"] = fulldepth
            
        return atts    
        
    
    
