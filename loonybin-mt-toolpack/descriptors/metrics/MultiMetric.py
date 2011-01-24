#!/usr/bin/env python
from loonybin import Tool

class MultiMetric(Tool):
    
    def getName(self):
        return "Machine Translation/Scoring/MultiMetric (BLEU, METEOR, TER)"
        
    def getDescription(self):
        return "Runs BLEU, METEOR, and TER on a set of hypotheses after passing them through Greg's detokenization script. Results are added to the .loon log file."
    
    def getRequiredPaths(self):
        return ['scoring-scripts', 'mt-analyzers']

    def getInputNames(self, params):
        return [ ('refs', 'Plaintext "laced" references, one per line with all references for the first sentence coming before the second sentence, etc.'),
                ('hyps','Plaintext hypotheses, one per line') ]

    def getOutputNames(self, params):
        return [ ('scoresOut','space-delimited list of several scores'),
                 ('meteorOut', 'aggregate METEOR score as a float'),
                 ('bleuOut', 'aggregate BLEU score as a float'),
                 ('terOut','aggregate TER score as a float') ]
    
    def getCommands(self, params, inputs, outputs):
        # multimetric.sh refs hyps scoresOut
        commands = []
        commands.append('JAVA_TOOL_OPTIONS="-Xmx1G" score.rb --hyp-detok %(hyps)s --refs-laced %(refs)s --output out.'%inputs)
        commands.append('mv out.scores %(scoresOut)s'%outputs)
        commands.append('mv out.meteor_out %(meteorOut)s'%outputs)
        commands.append('mv out.bleu_out %(bleuOut)s'%outputs)
        commands.append('mv out.ter_out.sum %(terOut)s'%outputs)
        return commands

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ 'multimetric-analyze.py %(meteorOut)s %(bleuOut)s %(terOut)s'%outputs ]

import sys
t = MultiMetric()
t.handle(sys.argv)
