'''
Feature generator for occurrences of parsing labels with the possibility to match equivalent labels across languages 
Created on 22 March 2011

@author: Eleftherios Avramidis
'''

from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
from numpy import average, std


class ParserMatches(LanguageFeatureGenerator):
    '''
    Read an existing parse in source and target language and count feature generator for occurrences 
    of parsing labels with the possibility to match equivalent labels across languages, so that
    per-label source/target ratios can be calculated
    @ivar mapping: A dictionary for mapping source labels to target labels
    @type mapping: dict 
    '''
    mapping = {}
    mapping[("de","en")] = [(["NP"], ["NP"]),
              (["VP", "VZ"], ["VP"]),
              (["VVFIN", "VAFIN",  "VMFIN", "VAINF", "VVINF" ,"VVPP" ], ["VB", "VBZ", "VBP", "VBN", "VBG" ]),
              (["NN", "NE"], ["NN", "NNP", "NNS"]),
              (["PP"], ["PP"]),
              (["$."], ["."]),
              (["$,"], [","])]
    
    mapping[("en","fr")] = [(["S", "SQ"], ["SENT", "Sint"]),
              (["SBAR"], ["Srel", "Ssub"]),
              (["NP"], ["NP"]),
              (["VP"], [ "VP", "VN", "VPinf", "VPpart" ]),
              (["VB", "VBZ", "VBP", "VBN", "VBG" ], ["V"]),
              (["NN", "NNP", "NNS"], ["N"] ),
              (["PP"], ["PP"]),
              (["ADVP"] , ["AdP"]),
              (["PRP"], ["CL"]),
              (["DT", "PRP$"], ["D"]),
              (["RB"], ["ADV"]),
              (["JJ"], ["A"]),
              (["."], ["."]),
              ([","], [","])]
    
    mapping[("de","fr")] = [(["NP"], ["NP"]),
              (["S"], ["SENT", "Srel", "Ssub"]),
              (["ART"], ["D"]),
              (["VP", "VZ"], ["VP", "VPinf"]),
              (["VVFIN", "VAFIN",  "VMFIN", "VAINF", "VVINF" ,"VVPP" ], ["V"]),
              (["NN", "NE"], ["N"] ),
              (["PP"], ["PP"]),
              (["$."], ["."]),
              (["$,"], [","])]
    
    mapping[("es","en")] = [(["sn"], ["NP"]),
              (["grup.verb"], ["VP"]),
              (["S"], ["S"]),
              (["v" ], ["VB", "VBZ", "VBP", "VBN", "VBG" ]),
              (["n"], ["NN", "NNP", "NNS"]),
              (["sp"], ["PP"]),
              (["pu"], ["."]),
              (["conj"], ["CC"]),
              (["a"], ["JJ"]),
              (["d"], ["DT", "PRP$"]),
              ([","], [","])]



    

    def __init__(self, langpair=("de","en")):
        '''
        Instantiate a parse label matcher for a particular language pair
        @param langpair: a tuple with the source and the target language codes
        @type langpair: (str, str)
        '''
        #reverse mappings as well
        reversed_mapping = {}
        for (source_language, target_language), mapping in self.mapping.iteritems():
            
            reversed_mapping[(target_language, source_language)] = [(target_mapping, source_mapping) for (source_mapping, target_mapping) in mapping] 

        self.mapping.update(reversed_mapping)
        self.mappings = self.mapping[langpair]
        
        
    
    def _count_nodetags(self, treestring="", taglist=[]):
        """
        Internal convenience function for shallow counting the the node labels in the given treestring
        @param treestring: a Berkeley bracketed PCFG parse
        @type treestring: str
        @param taglist: a list of tags to be processed
        @type taglist: [str, ...]
        @return: the count and the positions for the given tags
        @rtype: (int, [int, ...])
        """
        match_count = 0
        match_pos = [] 
        labels = treestring.split() 
        for parse_tag in taglist:
            parse_tag = "(%s" %parse_tag #get the bracket so that you can search in the parse string
            match_count += labels.count(parse_tag)
            for pos, label in enumerate(labels, start=1):
                if parse_tag == label:
                    match_pos.append(pos)
        if not match_pos:
            match_pos = [0]
        return match_count, match_pos

    def get_features_src(self, simplesentence, parallelsentence):
        attributes = {}
        try:
            src_parse = simplesentence.get_attribute("berkeley-tree")
        except:
            print "error reading berkeley tree"
            return {}
        for (src_map, tgt_map) in self.mappings:
            src_map_count, src_map_pos = self._count_nodetags(src_parse, src_map)
            src_label = self._canonicalize(src_map[0])
            attributes["parse-%s" % src_label] = str(src_map_count)   
            attributes["parse-%s-pos-avg" % src_label] = str(average(src_map_pos))
            attributes["parse-%s-pos-std" % src_label] = str(std(src_map_pos))
        return attributes
            
            
    def get_features_tgt(self, simplesentence, parallelsentence):
        attributes = {}
        try:
            tgt_parse = simplesentence.get_attribute("berkeley-tree")
        except:
            tgt_parse = ""
        try:
            src_parse = parallelsentence.get_source().get_attribute("berkeley-tree")
        except:
            src_parse = ""
        
        if tgt_parse and src_parse:
            for (src_map, tgt_map) in self.mappings:
                #src_label = self._canonicalize(src_map[0])
                #src_map_count = int(parallelsentence.get_source().get_attribute("parse-%s" % src_label))
                tgt_map_count, tgt_map_pos = self._count_nodetags(tgt_parse, tgt_map)
                tgt_label = self._canonicalize(src_map[0])
                attributes["parse-%s" % tgt_label] = str(tgt_map_count)
                attributes["parse-%s-pos-avg" % tgt_label] = str(average(tgt_map_pos))
                attributes["parse-%s-pos-std" % tgt_label] = str(std(tgt_map_pos))
#                if tgt_map_count != 0:
#                    attributes["parse-%s_ratio" % tgt_label] = str(1.0 * src_map_count / tgt_map_count)
#                else:
#                    attributes["parse-%s_ratio" % tgt_label] = str(float("Inf"))
        return attributes
        

    def _canonicalize(self, string):
        '''
        Internal convenience function for replacing node label characters 
        that are not valid XML arguments
        @param string: the label which needs be canonicalized
        @type string: str
        @return: illegal XML labels replaced
        @rtype: str
        '''
        string = string.replace("$." , "dot").replace("$," , "comma")
        string = string.replace(".", "dot").replace("," , "comma")
        return string
        