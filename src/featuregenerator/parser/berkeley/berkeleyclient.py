import xmlrpclib 
import base64
from featuregenerator.featuregenerator import FeatureGenerator
 
class BerkeleyFeatureGenerator(FeatureGenerator):
    '''
    classdocs
    '''


    def __init__(self, url):
        '''
        Constructor
        '''
        self.s = xmlrpclib.Server(url)
        
    def get_features_sentence(self, simplesentence, parallelsentence):
        sent_string = simplesentence.get_string()
        print self.s.parse ( sent_string )
        return None