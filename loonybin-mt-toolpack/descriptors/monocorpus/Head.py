from loonybin import Tool

class Head(Tool):
    def getName(self):
        return 'Machine Translation/Monolingual Corpus/Head'
    
    def getDescription(self):
        return "Takes 1 input monolingual corpus and returns the first n lines of it"
    
    def getRequiredPaths(self):
        return [ 'mt-analyzers' ]

    def getParamNames(self):
        return [ ('numLines', 'number of lines to take from the head of the corpus') ]
    
    def getInputNames(self, params):
        return [ ('corpus', 'corpus, one sentence per line') ]

    def getOutputNames(self, params):
        return [ ('corpus', 'first n lines of corpus') ]
    
    def getCommands(self, params, inputs, outputs):        
        return [ 'head -n %s %s '%(params['numLines'], inputs['corpus']) +
               '> %(corpus)s'%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ 'AnalyzeMonoCorpus.sh %(corpus)s'%outputs ]

if __name__ == '__main__':
    import sys
    t = Head()
    t.handle(sys.argv)
