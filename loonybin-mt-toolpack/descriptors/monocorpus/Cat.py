from loonybin import Tool

class Cat(Tool):
    def getName(self):
        return 'Machine Translation/Monolingual Corpus/Concatenate'
    
    def getDescription(self):
        return "Takes 2 input monolingual corpora and produces a single concatenated corpus"
    
    def getRequiredPaths(self):
        return ['mt-analyzers']
    
    def getInputNames(self, params):
        return [ ('corpus1', 'foreign side of parallel corpus, one sentence per line'),
                 ('corpus2', 'foreign side of parallel corpus, one sentence per line') ]

    def getOutputNames(self, params):
        return [ ('corpusOut', 'foreign side of parallel corpus, one sentence per line') ]
    
    def getCommands(self, params, inputs, outputs):        
        return [ 'cat %(corpus1)s %(corpus2)s'%inputs +
               '> %(corpusOut)s'%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ 'AnalyzeMonoCorpus.sh %(corpusOut)s'%outputs ]

if __name__ == '__main__':
    import sys
    t = Cat()
    t.handle(sys.argv)
