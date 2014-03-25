'''
Created on 22 March 2011

@author: Eleftherios Avramidis
'''

from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator



class ParserMatches(LanguageFeatureGenerator):
    '''
    classdocs
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
        Constructor
        '''
        #reverse mappings as well
        reversed_mapping = {}
        for (source_language, target_language), mapping in self.mapping.iteritems():
            
            reversed_mapping[(target_language, source_language)] = [(target_mapping, source_mapping) for (source_mapping, target_mapping) in mapping] 

        self.mapping.update(reversed_mapping)
        self.mappings = self.mapping[langpair]
        
        
    
    def _count_nodetags(self, treestring="", taglist=[]):
        match_count = 0
        for parse_tag in taglist:
            parse_tag = "(%s" %parse_tag #get the bracket so that you can search in the parse string
            match_count += treestring.count(parse_tag)
        return match_count

    def get_features_src(self, simplesentence, parallelsentence):
        attributes = {}
        try:
            src_parse = simplesentence.get_attribute("berkeley-tree")
        except:
            print "error reading berkeley tree"
            return {}
        for (src_map, tgt_map) in self.mappings:
            src_map_count = self._count_nodetags(src_parse, src_map)
            src_label = self._canonicalize(src_map[0])
            attributes["parse-%s" % src_label] = str(src_map_count)    
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
                tgt_map_count = self._count_nodetags(tgt_parse, tgt_map)
                tgt_label = self._canonicalize(src_map[0])
                attributes["parse-%s" % tgt_label] = str(tgt_map_count)
#                if tgt_map_count != 0:
#                    attributes["parse-%s_ratio" % tgt_label] = str(1.0 * src_map_count / tgt_map_count)
#                else:
#                    attributes["parse-%s_ratio" % tgt_label] = str(float("Inf"))
        return attributes
        

    def _canonicalize(self, string):
        string = string.replace("$." , "dot").replace("$," , "comma")
        string = string.replace(".", "dot").replace("," , "comma")
        return string
        
        
        
                    
                    
                    
                    
                     
    
        
