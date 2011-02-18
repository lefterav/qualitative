import xmlrpclib 
import base64
from featuregenerator.featuregenerator import FeatureGenerator
 

'''
Created on Feb 15, 2011

@author: elav01
'''

class BerkeleyFeatureGenerator(FeatureGenerator):
    '''
    classdocs
    '''


    def __init__(self, url):
        '''
        Constructor
        '''
        
        self.s = xmlrpclib.Server(url)
    
    