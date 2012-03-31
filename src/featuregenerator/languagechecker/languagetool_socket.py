'''
Created on 30 Mar 2012

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


    def __init__(self, lang, socket):
        '''
        Constructor
        '''
        self.lang = lang
        
        gatewayclient = socket
        gateway = JavaGateway(gatewayclient)
        ltool_view = gateway.new_jvm_view()
        java_import(ltool_view, 'org.languagetool.*')
        
        tool_language = ltool_view.Language.getLanguageForShortName(lang)
        self.ltool = ltool_view.JLanguageTool(tool_language)
        self.ltool.activateDefaultPatternRules();
        
        
    def get_features_string(self, string):
        atts = {}
        matches = self.ltool.check(string)
        errors = 0
        total_error_chars = 0
        for match in matches:
            error_id = "lt_{}".format(match.getRule().getId())
            try:
                atts[error_id] += 1
            except KeyError:
                atts[error_id] = 1
            errors += 1
            
            error_chars = match.getEndColumn() - match.getColumn()
            error_chars_id = "lt_{}_chars".format(error_id)
            try:
                atts[error_chars_id] += error_chars
            except KeyError:
                atts[error_chars_id] = error_chars
            total_error_chars += error_chars
            
            #make every value a string    
        for k,v in atts.iteritems():
            atts[k] = str(v)
        
        atts["lt_errors"] = str(errors)
        atts["lt_errors_chars"] = str(total_error_chars)
        
        return atts
            
    
        
        
    
