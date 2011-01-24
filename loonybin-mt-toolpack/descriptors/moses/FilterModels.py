#!/usr/bin/env python
from loonybin import Tool
from Moses import Moses

class FilterModels(Tool):

    def __init__(self):
        self.moses = Moses()

    def getName(self):
        return 'Machine Translation/Grammars and Tables/Local/Filter Models Given Input'
    
    def getDescription(self):
        return "Filters a phrase table (and distortion model) to an input"
    
    def getRequiredPaths(self):
        return ['moses']

    def getParamNames(self):
        return []

    def getInputNames(self, params):
        return [ ('roFile','Moses-format phrase table'),
                 ('ptFile','Moses-format distortion model'),
                 ('inputSentences','sentences to which models will be filtered') ]

    def getOutputNames(self, params):   
        return [ ('filteredPhraseTable', 'Moess-format phrase table, valid only for input sentences'),
                 ('filteredReorderingModel','Moses-format distortion model, valid only for input sentences') ]

    def getCommands(self, params, inputs, outputs):

        # Give some dummy values to moses.ini since it doesn't affect the filtering
        inputs['lmFile'] = 'DUMMY'
        params['lmLibrary'] = 'srilm'
        params['lmOrder'] = '0'
        params['ttableLimit'] = '0'
        params['distortionLimit'] = '0'

        params['roModelType'] = 'msd-bidirectional-fe' # Script actually doesn't use this
        commands = []
        commands.append('ln -s %(roFile)s roFile'%inputs)
        params['roFile'] = 'roFile'

        commands.extend( self.moses.makeConfigFileCommands(params, inputs, 'moses.ini') )
        commands.append('./scripts/training/filter-model-given-input.pl filteredDir moses.ini %(inputSentences)s'%inputs)
        commands.append('ln -s `pwd`/filteredDir/phrase-table.0-0.1* %(filteredPhraseTable)s'%outputs)
        commands.append('ln -s `pwd`/filteredDir/roFile %(filteredReorderingModel)s'%outputs)
        return commands

import sys
t = FilterModels()
t.handle(sys.argv)
