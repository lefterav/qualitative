import xmlrpclib 
import base64
from featuregenerator.featuregenerator import FeatureGenerator
 

class SRILMFeatureGenerator(FeatureGenerator):
    '''
    Allows communication with the SRILM server of Nitin Madnani 
    '''


    def __init__(self, url):
        '''
        Define connection with the server
        '''
        self.s = xmlrpclib.Server(url)
        
    def get_features_sentence(self, simplesentence, parallelsentence):
        """
        
        """
        sent_string = simplesentence.get_string()
        l = len(sent_string.split(" "))
        attributes = {}
        
   
        #print l, sent_string
        sentProb = self.s.getSentenceProb(base64.standard_b64encode(sent_string), l)
        attributes["prob"] = str(sentProb)
        return attributes
