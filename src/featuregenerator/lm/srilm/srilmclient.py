import xmlrpclib 
import base64
from featuregenerator.featuregenerator import FeatureGenerator
 

class SRILMFeatureGenerator(FeatureGenerator):
    '''
    Allows communication with the SRILM server of Nitin Madnani 
    '''
    
    def __init__(self, url, lang):
        '''
        Define connection with the server
        '''
        self.server = xmlrpclib.Server(url)
        self.lang = lang
        
    
    def add_features_src(self, simplesentence, parallelsentence):
        src_lang = parallelsentence.get_attribute("langsrc")
        if src_lang == self.lang:
            prob = self.__get_sentence_probability__(simplesentence)
            simplesentence.add_attribute("prob", prob)
        return simplesentence

    def add_features_tgt(self, simplesentence, parallelsentence):
        tgt_lang = parallelsentence.get_attribute("langtgt")
        if tgt_lang == self.lang:
            prob = self.__get_sentence_probability__(simplesentence)
            simplesentence.add_attribute("prob", prob)
        return simplesentence        
        
    def __get_sentence_probability__(self, simplesentence ):
        sent_string = simplesentence.get_string()
        l = len(sent_string.split(" "))       
   
        #print l, sent_string
        return str (self.server.getSentenceProb(base64.standard_b64encode(sent_string), l))
        
