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
    
    mapping[("en","fr")] = [(["S"], ["SENT", "Sint"]),
              (["SBAR"], ["Srel", "Ssub"]),
              (["NP"], ["NP"]),
              (["VP"], [ "VP", "VN", "VPinf", ]),
              (["VB", "VBZ", "VBP", "VBN", "VBG" ], ["V"]),
              (["NN", "NNP", "NNS"], ["N"] ),
              (["PP"], ["PP"]),
              (["$."], ["."]),
              (["$,"], [","])]
    


    def __init__(self, langpair=("de","en")):
        '''
        Constructor
        '''
        self.mappings = self.mapping[langpair]
    
    def __count_nodetags__(self, treestring="", taglist=[]):
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
            src_map_count = self.__count_nodetags__(src_parse, src_map)
            src_label = self.__canonicalize__(src_map[0])
            attributes["parse-%s" % src_label] = str(src_map_count)
            print "adding attribute" , "parse-%s" % src_label , "=" ,str(src_map_count)
    
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
                #src_label = self.__canonicalize__(src_map[0])
                #src_map_count = int(parallelsentence.get_source().get_attribute("parse-%s" % src_label))
                tgt_map_count = self.__count_nodetags__(tgt_parse, tgt_map)
                tgt_label = self.__canonicalize__(src_map[0])
                attributes["parse-%s" % tgt_label] = str(tgt_map_count)
#                if tgt_map_count != 0:
#                    attributes["parse-%s_ratio" % tgt_label] = str(1.0 * src_map_count / tgt_map_count)
#                else:
#                    attributes["parse-%s_ratio" % tgt_label] = str(float("Inf"))
        return attributes
        

    def __canonicalize__(self, string):
        string = string.replace("$." , "dot").replace("$," , "comma")
        string = string.replace(".", "dot").replace("," , "comma")
        return string
        
        
        
                    
                    
                    
                    
                     
    
        
