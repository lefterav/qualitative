#!/usr/bin/env python
from loonybin import Tool
from libmoses import *

class LearnLex(Tool):

    def getName(self):
        return 'Machine Translation/Grammars and Tables/Local/Learn Lexicalized Reordering Model'
    
    def getDescription(self):
        return "Extracts phrase instances using the standard Moses script"
    
    def getRequiredPaths(self):
        return ['moses']

    def getParamNames(self):
        return [ ('roModelType','one of '+RO_MODEL_TYPES) ]

    def getInputNames(self, params):
        return [ ('phraseInstanceOrientations', '?') ]

    def getOutputNames(self, params):   
        return [ ('scoredReorderingTable','?') ]

    def getCommands(self, params, inputs, outputs):     
        commands = getDummyMosesCommands()
        # TODO: Symlink both directions of lexicons and extract files to roots
        # Double check order of inv and lexE2F

        # Assign $script variable
        commands.extend( getMosesScriptFinder() )
        commands.append('ln -s %(phraseInstanceOrientations)s ext.o'%inputs)
        commands.append(
                '$script --first-step 7 --last-step 7 --bin-dir dummyBin --f f --e e --model-dir .'+
                ' --reordering %(roModelType)s'%params+
                ' --extract-file ext'%inputs+
                ' --reordering-table ro')
        commands.append('# Unzip for now until Moses supports not zipping or LoonyBin supports gzip -- This file could be ro.gz in older versions of ro.MODEL_TYPE.gz in newer versions')
        commands.append('zcat ro*gz > %(scoredReorderingTable)s'%outputs)
        return commands

import sys
t = LearnLex()
t.handle(sys.argv)
