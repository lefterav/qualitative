#!/usr/bin/env python
from loonybin import Tool

class SymmetrizeWordAlignments(Tool):
    
    def __init__(self):
        self.validHeuristics = [ 'intersection', 'grow', 'grow-diag', 'grow-diag-final',
                             'grow-diag-final-and', 'union', 'srctotgt', 'tgttosrc' ]

    def getName(self):
        return 'Machine Translation/Word Alignment/Symmetrize Word Alignments'
    
    def getDescription(self):
        return "Uses symal to symmetrize alignments (combine the 2 directional GIZA alignments) according to the Koehn heuristics."
    
    def getRequiredPaths(self):
        return ['moses', 'mt-analyzers']

    def getParamNames(self):
        return [ ('heuristic', 'one of ' + ' '.join(self.validHeuristics)) ]

    def getInputNames(self, params):
        return [ ('src2tgtA3final', 'source to target A3 final file from GIZA++'),
                 ('tgt2srcA3final', 'target to source A3 final file from GIZA++') ]

    def getOutputNames(self, params):
        return [ ('symmetrizedAlignment', 'Symmetrized alignment in moses format: srcIndex-tgtIndex ...') ]


    def getCommands(self, params, inputs, outputs):
        
        heuristic = params['heuristic']
        if heuristic not in self.validHeuristics:
            raise Exception('Invalid value for heuristic: ' + heuristic)
              
        if 'union' == heuristic:
            symalA = 'union'
        elif 'intersect' in heuristic:
            symalA = 'intersect'
        elif 'grow' in heuristic:
            symalA = 'grow'
        elif 'srctotgt' in heuristic:
            symalA = 'srctotgt'
        elif 'tgttosrc' in heuristic:
            symalA = 'tgttosrc'            
         
        symalD = 'yes' if 'diag' in heuristic else 'no'
        symalF = 'yes' if 'final' in heuristic else 'no'
        symalB = 'yes' if 'final-and' in heuristic else 'no'

        return [ './scripts/training/symal/giza2bal.pl -d %(src2tgtA3final)s -i %(tgt2srcA3final)s '%inputs + 
                  '| ./scripts/training/symal/symal -alignment=%s -diagonal=%s -final=%s -both=%s '%(symalA, symalD, symalF, symalB) +
                  '> %(symmetrizedAlignment)s'%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
#        cmd1 = ('AnalyzeAlignments.py %(x)s'%outputs) # Calculate crossings, etc.
#        return [ cmd1, cmd2 ]
        return []

import sys
t = SymmetrizeWordAlignments()
t.handle(sys.argv)
