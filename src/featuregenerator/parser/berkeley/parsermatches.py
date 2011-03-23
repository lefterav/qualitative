'''
Created on 22 March 2011

@author: Eleftherios Avramidis
'''

from featuregenerator.featuregenerator import FeatureGenerator



class ParserMatches(FeatureGenerator):
    '''
    classdocs
    '''
    self.mappings=[(["NP"], ["NP"]),
              (["VP", "VZ"], ["VP"]),
              (["VVFIN", "VAFIN",  "VMFIN", "VAINF", "VVINF" ,"VVPP" ], ["VB", "VBZ", "VBP", "VBN", "VBG" ]),
              (["NN", "NE"], ["NN", "NNP", "NNS"])
              (["PP"], ["PP"])]
    

    def __init__(self, params=[]):
        '''
        Constructor
        '''
    
    def add_features_tgt(self, simplesentence, parallelsentence):
        tgt_parse = simplesentence.get_attribute("berkeley-tree")
        src_parse = parallelsentence.get_source().get_attribute("berkeley-tree")
        if tgt_parse and src_parse:
            src_map_count = 0
            tgt_map_count = 0
            
            for (src_map, tgt_map) in self.mappings:
                tree_tag = "(%s"% tgt_map
                tgt_parse.count() 
                    
                     
    
        