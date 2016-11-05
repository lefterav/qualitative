'''
Wrapper and feature generator for LanguageTool via a Py4J socket 
Created on 30 Mar 2012

@author: Eleftherios Avramidis
'''
from py4j.java_gateway import java_import
from featuregenerator import LanguageFeatureGenerator
import numpy as np
from collections import defaultdict
from time import sleep
import logging as log

class LanguageToolSocketFeatureGenerator(LanguageFeatureGenerator):
    '''
    Feature generator for the Language Tool, providing rule-based language suggestion
    Language tool is wrapped via JVM and loaded on the background
    The sentence is analyzed and the count of specific errors, error types and total sentence
    errors are added as features, along with their length as characters.
    @ivar ltoot: the JVM object of the LanguageTool
    @type ltool: org.languagetool.JLanguageTool as described in LanguageTool Java API
    '''
    feature_patterns = ['lt_.*']

    def __init__(self, language, gateway, **kwargs):
        '''
        Constructor
        '''
        self.language = language
        ltool_view = gateway.new_jvm_view()
        java_import(ltool_view, 'org.languagetool.Languages')
        java_import(ltool_view, 'org.languagetool.JLanguageTool')

        if language=='ru':
            language = 'ru-RU' 
        
        tool_language = ltool_view.Languages.getLanguageForShortName(language)
        self.ltool = ltool_view.JLanguageTool(tool_language)        
        
    def get_features_string(self, string):
        atts = {}
        tries = 0
        found = False
        while tries < 10 and not found:
            tries+=1
            try:
                log.debug("Language tooltrying on effort {}.".format(tries))
                matches = self.ltool.check(string)
                found = True
            except Exception as e:
                log.debug("Language tool crashed on effort {}. Trying again. Error given {}".format(tries, e))
                sleep(1)
        if not found:
            return {}
        errors = 0
        total_error_chars = 0
        total_replacements = 0
        seen_categories = set()
        seen_issue_types = set()
        replacements = defaultdict(list)
        for match in matches:
            error_id = "err_{}".format(match.getRule().getId())
            atts[error_id] = atts.setdefault(error_id, 0) + 1

            errors += 1
            category_name = unicode(match.getRule().getCategory())
            category_id = "cat_{}".format(category_name.encode('ascii', 'ignore'))
            atts[category_id] = atts.setdefault(category_id, 0) + 1
            seen_categories.add(category_id)
            
            issue_type = "issue_{}".format(match.getRule().getLocQualityIssueType().toString())
            atts[issue_type] = atts.setdefault(issue_type, 0) + 1
            seen_issue_types.add(issue_type)
            
            error_chars = match.getEndColumn() - match.getColumn()
            error_chars_key = "{}_chars".format(error_id)
            atts[error_chars_key] = atts.setdefault(error_chars_key, 0) + error_chars
            
            total_error_chars += error_chars
            
            error_replacements_key = "{}_replacements".format(error_id)
            this_replacements = match.getSuggestedReplacements()
            total_replacements += len(this_replacements)
            replacements[error_id].extend(this_replacements)
            
            atts[error_replacements_key] = atts.setdefault(error_replacements_key, 0) + len(replacements[error_id])
            total_replacements += len(this_replacements)
            avgchars = np.average([len(replacement) for replacement in replacements[error_id]])
            atts["{}_replacements_avgchars".format(error_id)] = avgchars
            
        atts["errors"] = errors
        atts["errors_chars"] = total_error_chars
        atts["replacements"] = total_replacements
        atts["categories"] = len(seen_categories)
        atts["issuetypes"] = len(seen_issue_types)
        
        prefixed_atts = {}
        for k,v in atts.iteritems():
            prefixed_atts["lt_{}".format(k)] = v
        
        return prefixed_atts
            
