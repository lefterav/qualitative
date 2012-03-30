'''
Created on 30 Mar 2012

@author: elav01
'''
from py4j.java_gateway import JavaGateway
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
from py4j.java_gateway import java_import

class IqSocketFeatureGenerator(LanguageFeatureGenerator):
    '''
    classdocs
    '''


    def __init__(self, lang):
        '''
        Constructor
        '''
        self.lang = lang
        
        gateway = JavaGateway()
        module_view = gateway.new_jvm_view()
        java_import(module_view, 'org.languagetool.*')
        
        english = module_view.Language.getLanguageForShortName(lang)
        self.ltool = module_view.JLanguageTool(english)
        
        
    def get_features_string(self, string):
        matches = self.ltool.check(string)
        
        
    
