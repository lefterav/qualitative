'''
Wrapper and feature generator for LanguageTool via a Py4J socket 
Created on 30 Mar 2012

@author: Eleftherios Avramidis
'''
from py4j.java_gateway import java_import
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
import numpy as np
from collections import defaultdict

class LanguageToolSocketFeatureGenerator(LanguageFeatureGenerator):
    '''
    Feature generator for the Language Tool, providing rule-based language suggestion
    '''

    def __init__(self, lang, gateway):
        '''
        Constructor
        '''
        self.lang = lang
        ltool_view = gateway.new_jvm_view()
        java_import(ltool_view, 'org.languagetool.Languages')
        java_import(ltool_view, 'org.languagetool.JLanguageTool')

        if lang=='ru':
            lang = 'ru-RU' 
        
        tool_language = ltool_view.Languages.getLanguageForShortName(lang)
        self.ltool = ltool_view.JLanguageTool(tool_language)        
        
    def get_features_string(self, string):
        atts = {}
        matches = self.ltool.check(string)
        errors = 0
        total_error_chars = 0
        total_replacements = 0
        replacements = defaultdict(list)
        for match in matches:
            error_id = match.getRule().getId()
            atts[error_id] = atts.setdefault(error_id, 0) + 1

            errors += 1
            
            category_id = match.getRule().getCategory().getName()
            atts[category_id] = atts.setdefault(category_id, 0) + 1
            
            issue_type = match.getRule().getLocQualityIssueType().toString()
            atts[issue_type] = atts.setdefault(issue_type, 0) + 1
            
            error_chars = match.getEndColumn() - match.getColumn()
            error_chars_key = "{}_chars".format(error_id)
            atts[error_chars_key] = atts.defaultdict(error_chars_key, 0) + error_chars
            
            total_error_chars += error_chars
            
            error_replacements_key = "{}_replacements".format(error_id)
            this_replacements = match.getSuggestedReplacements()
            replacements[error_id].extend(this_replacements)
            
            atts[error_replacements_key] = atts.setdefault(error_replacements_key, 0) + len(replacements[error_id])
            total_replacements += len(this_replacements)
            avgchars = np.average([len(replacement) for replacement in replacements[error_id]])
            atts["{}_replacements_avgchars".format(error_id)] = avgchars
            
        atts["errors"] = str(errors)
        atts["errors_chars"] = str(total_error_chars)
        
        for k,v in atts.iteritems():
            atts["lt_{}".format(k)] = v
        
        return atts
            
    
#    def __del__(self):
#        self.jvm.terminate()
