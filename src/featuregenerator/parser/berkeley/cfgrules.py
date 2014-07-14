'''
Created on Jul 13, 2014

@author: Eleftherios Avramidis
'''
import logging
from featuregenerator.featuregenerator import FeatureGenerator

class Rule:
    def __init__(self):
        self.lhs = None
        self.rhs = []
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
            nextrule = Rule()
            label = []
            
        #space indicates the label is finished and can be 
        #attached to the previous rule as a child (RHS)
        #and the new rule as a head (LHS)
        elif char==" " and prevchar != ")": #not after a closing bracket
            labelstr = "".join(label)
            previousrule.rhs.append(labelstr)
            nextrule.lhs = labelstr
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

    def __init__(self, params):
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
        for rule in cfg_rules:
            atts[rule] =  atts.setdefault(rule, 0) + 1
        return atts    
        
    
    
