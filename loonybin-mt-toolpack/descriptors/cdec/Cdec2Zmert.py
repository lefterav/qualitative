from loonybin import Tool

class Cdec2Zmert(Tool):
    
    def getName(self):
        return 'Machine Translation/Reranking/Cdec to Zmert Converter'
    
    def getDescription(self):
        return "Converts a cdec n-best list and weights file into the format expected by Z-MERT for reranking"
    
    def getRequiredPaths(self):
        return ['cdec']

    def getParamNames(self):
        return []

    def getInputNames(self, params):
        return [ ('cdecNbest','Cdec-format n-best list'),
                 ('cdecFeats','Cdec-format feature weights file') ]

    def getOutputNames(self, params):
        return [ ('zmertNbest','Z-MERT format n-best list'),
                 ('zmertParamConfig','Z-MERT format feature weight space config file'),
		 ('zmertWeights', 'Z-MERT weight names (to be used as the "decoder config")') ]

    def getPreAnalyzers(self, params, inputs):
        return [ ]
    
    def getCommands(self, params, inputs, outputs):
        return [ './rescore/cdec_kbest_to_zmert.pl -f %(cdecFeats)s -h %(cdecNbest)s'%inputs
                 + ' > %(zmertNbest)s'%outputs,
                 './rescore/generate_zmert_params_from_weights.pl < %(cdecFeats)s'%inputs
                 + ' > %(zmertFeats)s'%outputs,
		'cp %s %s'%(inputs['cdecFeats'], outputs['zmertWeights']) ]

    def getPostAnalyzers(self, params, inputs, outputs):
	return [ ]

if __name__ == '__main__':
    import sys
    t = Cdec2Zmert()
    t.handle(sys.argv)
