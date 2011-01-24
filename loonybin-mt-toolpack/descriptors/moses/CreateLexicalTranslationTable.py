#!/usr/bin/env python
from loonybin import Tool
from libmoses import *

class CreateLexTable(Tool):

    def getName(self):
        return 'Machine Translation/Grammars and Tables/Local/Create Unigram Lexical Translation Table'
    
    def getDescription(self):
        return "Extracts a unigram translation table"
    
    def getRequiredPaths(self):
        return ['moses']

    def getParamNames(self):
        return [ ]

    def getInputNames(self, params):
        return [ ('fCorpus','x'),
                 ('eCorpus','x'),
                 ('symmetrizedAlignment','?') ]

    def getOutputNames(self, params):   
        return [ ('lexF2E', 'MLE-estimated lexical probabilities'),
                 ('lexE2F', 'MLE-estimated lexical probabilities') ]

    def getCommands(self, params, inputs, outputs):     
        
        # TODO: Create executable mkcls, GIZA++, and snt2cooc.out
        # TODO: Create model directory
        # copy alignments to model/aligned.grow-diag-final
        # ../train-factored-phrase-model.perl --corpus x --e e --f f --first-step 4 --last-step 4 --bin-dir .
        # output is in ./model/lex.0-0.f2e and ./model/lex.0-0.e2f
        
        commands = getDummyMosesCommands()
        # Assign $script variable
        commands.extend( getMosesScriptFinder() )
        commands.extend([
                'ln -s %(symmetrizedAlignment)s aligned.grow-diag-final'%inputs,
                    'ln -s %(eCorpus)s corpus.e'%inputs,
                    'ln -s %(fCorpus)s corpus.f'%inputs,
                    '$script --corpus corpus --e e --f f --first-step 4 --last-step 4 --bin-dir dummyBin --model-dir .',
                    '# Older versions use lex.0-0.f2e, newer versions just lex.f2e',
                    'ln -s `pwd`/lex*f2e %(lexF2E)s'%outputs,
                    'ln -s `pwd`/lex*e2f %(lexE2F)s'%outputs])
        return commands

import sys
t = CreateLexTable()
t.handle(sys.argv)
