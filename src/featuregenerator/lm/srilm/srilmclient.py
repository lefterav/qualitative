import xmlrpclib 
import base64
from featuregenerator.featuregenerator import FeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer

class SRILMFeatureGenerator(FeatureGenerator):
    '''
    Allows communication with the SRILM server of Nitin Madnani 
    '''
    
    def __init__(self, url, lang="en", lowercase=True, tokenize=True):
        '''
        Define connection with the server
        '''
        self.server = xmlrpclib.Server(url)
        self.lang = lang
        self.lowercase = lowercase
        self.tokenize = tokenize
        
    
    def get_features_src(self, simplesentence, parallelsentence):
        attributes = {}
        src_lang = parallelsentence.get_attribute("langsrc")
        if src_lang == self.lang:
            sent_string = self.__prepare_sentence__(simplesentence)
            prob = self.__get_sentence_probability__(sent_string)
            attributes = {"prob": prob}
            #print "Got src probability %s" % str(prob)
        else:
            #print "Src lang didn't match"
            pass
        return attributes

    def get_features_tgt(self, simplesentence, parallelsentence):
        attributes = {}
        tgt_lang = parallelsentence.get_attribute("langtgt")
        if tgt_lang == self.lang:
            sent_string = self.__prepare_sentence__(simplesentence)
            prob = self.__get_sentence_probability__(sent_string)
            attributes = {"prob": prob}
        return attributes        
    
    
    def __prepare_sentence__(self, simplesentence):
        sent_string = simplesentence.get_string().strip()
        if self.tokenize:
            tokenized_string = PunktWordTokenizer().tokenize(sent_string)
            sent_string = ' '.join(tokenized_string)
            
        if self.lowercase:
            sent_string = sent_string.lower()
        return sent_string
            
    
    def __get_sentence_probability__(self, sent_string ):
        
        l = len(sent_string.split(" "))       
   
        #print l, sent_string
        return str (self.server.getSentenceProb(base64.standard_b64encode(sent_string), l))


            
        
        
        
