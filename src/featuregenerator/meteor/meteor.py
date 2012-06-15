'''
Created on 15 Jun 2012

@author: elav01
'''

from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayClient
from py4j.java_gateway import java_import
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator

class LanguageToolSocketFeatureGenerator(LanguageFeatureGenerator):
    '''
    classdocs
    '''


#    def __init__(self, lang, classpath):
    def __init__(self, lang, gateway):
        '''
        Constructor
        '''
        self.lang = lang
    