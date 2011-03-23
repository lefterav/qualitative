#!/usr/bin/env python
from loonybin import Tool

class MultiMetric(Tool):
    
    def getName(self):
        return "Machine Translation/Scoring/MultiBleu (Moses)"
        
    def getDescription(self):
        return "Runs BLEU on a set of hypotheses."
    
    def getRequiredPaths(self):
        return ['moses-scripts']

    def getInputNames(self, params):
        return [ ('refs', 'Plaintext "laced" references, one per line with all references for the first sentence coming before the second sentence, etc.'),
                ('hyps','Plaintext hypotheses, one per line') ]

    def getOutputNames(self, params):
        return [ ('bleuOut', 'BLEU score ') ]
    
    def getCommands(self, params, inputs, outputs):
        # multimetric.sh refs hyps scoresOut
        commands = []
        command = 'perl ./generic/multi-bleu.perl %(refs)s < %(hyps)s '%inputs
        command += '>  %(bleuOut)s'%outputs
        commands.append(command)
        command = 'echo "Results: `cat %(bleuOut)s`" '
        commands.append(command)
        return commands


import sys
t = MultiMetric()
t.handle(sys.argv)
