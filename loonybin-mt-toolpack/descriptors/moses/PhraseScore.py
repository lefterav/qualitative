#!/usr/bin/env python
from loonybin import Tool
from libmoses import *

class PhraseScore(Tool):

    def getName(self):
        return 'Machine Translation/Grammars and Tables/Local/Score Phrases'
    
    def getDescription(self):
        return "Extracts phrase instances using the standard Moses script"
    
    def getRequiredPaths(self):
        return ['moses']

    def getParamNames(self):
        return [ ] # ('properConditioning','?')

    def getInputNames(self, params):
        return [ ('phraseInstances', '?'),
                 ('phraseInstancesInverse', '?'),
                 ('lexE2F', '?'),
                 ('lexF2E', '?') ]

    def getOutputNames(self, params):   
        return [ ('scoredPhraseTable','?') ]

    def getCommands(self, params, inputs, outputs):     
        commands = getDummyMosesCommands()
        # TODO: Symlink both directions of lexicons and extract files to roots
        # Double check order of inv and lexE2F

        # Assign script variable
        commands.extend( getMosesScriptFinder() )
        commands.extend([
                '# Link 0-0 variants for older versions',
                'ln -s %(lexE2F)s lex.0-0.e2f'%inputs,
                'ln -s %(lexF2E)s lex.0-0.f2e'%inputs,
                'ln -s %(phraseInstances)s ext.0-0'%inputs,
                'ln -s %(phraseInstancesInverse)s ext.0-0.inv'%inputs,

                '# Link variants without 0-0 for newer versions',
                'ln -s %(lexE2F)s lex.e2f'%inputs,
                'ln -s %(lexF2E)s lex.f2e'%inputs,
                'ln -s %(phraseInstances)s ext'%inputs,
                'ln -s %(phraseInstancesInverse)s ext.inv'%inputs,

                '$script --first-step 6 --last-step 6 --bin-dir dummyBin'+
                ' --lexical-file lex --extract-file ext --model-dir . --f f --e e'%inputs+
                ' --phrase-translation-table pt'%outputs])
        commands.append('gunzip pt.gz # Unzip for now until Moses supports not zipping or LoonyBin supports gzip')
        commands.append('mv pt %(scoredPhraseTable)s'%outputs)
        return commands

import sys
t = PhraseScore()
t.handle(sys.argv)
