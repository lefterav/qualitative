from loonybin import Tool

class PruneLM(Tool):
    
    def getName(self):
        return 'Machine Translation/Language Modeling/Prune Language Model'
    
    def getDescription(self):
        return "Prunes a Language Model using the Entropy-Based pruning method described in (Stolcke, 1998)."
    
    def getRequiredPaths(self):
        return ['srilm']

    def getParamNames(self):
        return [ ('relativeEntropyThreshold','Maximum relative perplexity decrease of overall model for removing n-gram probabilities (default:10e-8)'),
				 ('order','order of the language model (e.g. 3 for a trigram LM)') ]
    
    def getInputNames(self, params):
        return [ ('lm','ARPA format language model') ]

    def getOutputNames(self, params):
        return [ ('lm','pruned language model') ]
    
    def getCommands(self, params, inputs, outputs):
        return [ './ngram -prune %(relativeEntropyThreshold)s -order %(order)s'%params+
				 ' -lm %(lm)s'%inputs +
                 ' -write-lm %(lm)s'%outputs]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = PruneLM()
    t.handle(sys.argv)
