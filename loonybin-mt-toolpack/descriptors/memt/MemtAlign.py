from loonybin import Tool

class MemtDecode(Tool):
    
    def getName(self):
        return 'Machine Translation/MEMT/Align Topbest Hypotheses'
    
    def getDescription(self):
        return "Produce all pairwise alignments between hypotheses from the systems to combine using the METEOR matche"
    
    def getRequiredPaths(self):
        return ['memt']

    def getParamNames(self):
        return [ ('numSystems','Number of systems to be combined') ]

    def getInputNames(self, params):
        try:
            n = int(params['numSystems'])
        except:
            n = 0
        return [ ('topbestSystem%d'%i,'Topbest hypotheses for system %d'%i) for i in range(1,n+1) ]

    def getOutputNames(self, params):
        return [ ('alignedTopbestHypotheses', 'Aligned topbest hypotheses with all pairwise alignments between systems') ]
    
    def getCommands(self, params, inputs, outputs):
        n = int(params['numSystems'])
        inFiles = ' '.join([ inputs['topbestSystem%d'%i] for i in range(1,n+1) ])
        return [ './Alignment/match.sh ' + inFiles + ' > %(alignedTopbestHypotheses)s'%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = MemtDecode()
    t.handle(sys.argv)
