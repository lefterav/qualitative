from loonybin import Tool

class Rerank(Tool):
    
    def getName(self):
        return 'Machine Translation/Reranking/Cdec Reranker'
    
    def getDescription(self):
        return "Reranks a n-best list given a set of weights and provides the topbest output"
    
    def getRequiredPaths(self):
        return ['cdec']

    def getParamNames(self):
        return []

    def getInputNames(self, params):
        return [ ('nbestList','Cdec-format n-best list'),
                 ('weights','Cdec-format weights file') ]

    def getOutputNames(self, params):
        return [ ('topbest','Topbest hypothesis for each sentence within the given n-best list for the specified weights') ]

    def getPreAnalyzers(self, params, inputs):
        return [ ]
    
    def getCommands(self, params, inputs, outputs):
        return [ './rescore/rerank.pl -w %(weights)s -h %(nbestList)s'%inputs
                 + ' > %(topbest)s'%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
	return [ ]

if __name__ == '__main__':
    import sys
    t = Rerank()
    t.handle(sys.argv)
