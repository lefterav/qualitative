#!/usr/bin/env python
from loonybin import Tool

class PhraseExtract(Tool):

    def getName(self):
        return 'Machine Translation/Grammars and Tables/Local/Extract Phrases'
    
    def getDescription(self):
        return "Extracts phrase instances using the standard Moses script"
    
    def getRequiredPaths(self):
        return ['moses']

    def getParamNames(self):
        return [ ('maxPhraseLength','maximum number of tokens to be included in any extracted phrase'),
                 #('includeOrientation','include orientation information for building a MSD lexicalized reordering model') 
                 ]

    def getInputNames(self, params):
        return [ ('fCorpus','x'),
                 ('eCorpus','x'),
                 ('symmetrizedAlignment','?') ]

    def getOutputNames(self, params):   
        return [ ('phraseInstances', 'phrase instances in Moses format'),
                 ('phraseInstancesInverse','phrase instances in Moses format with source and target phrases in different columns'),
                 ('phraseInstanceOrientations', 'phrase instances with orientation information for creating a lexicalized reordering model') ]

    def getCommands(self, params, inputs, outputs):     
        # "$PHRASE_EXTRACT $alignment_file_e $alignment_file_f $alignment_file_a $extract_file $___MAX_PHRASE_LENGTH";
        # $cmd .= " --NoFileLimit" unless $_FILE_LIMIT;
        # $cmd .= " --ProperConditioning" if $_PROPER_CONDITIONING;

        orientation = ' orientation' #if params['includeOrientation'][0].lower() == 't' else ''
        
        return [ '# Hack to support older version of phrase extract that requires noFileLimit',
                 'if [[ "`(./scripts/training/phrase-extract/extract 2>&1) | fgrep -c NoFileLimit`" == "1" ]]; then noFileLimit="--NoFileLimit"; fi',
                 './scripts/training/phrase-extract/extract %(eCorpus)s %(fCorpus)s %(symmetrizedAlignment)s'%inputs +
                    ' %(phraseInstances)s'%outputs +
                    ' %(maxPhraseLength)s'%params +
                    ' $noFileLimit' +
                    orientation,
                    'mv %(phraseInstances)s.inv '%outputs + '%(phraseInstancesInverse)s'%outputs,
                    'mv %(phraseInstances)s.o '%outputs + '%(phraseInstanceOrientations)s'%outputs,
                     ]

import sys
t = PhraseExtract()
t.handle(sys.argv)
