from loonybin import Tool

class ParallelHead(Tool):
    def getName(self): return 'Machine Translation/Parallel Corpus/Head'
    def getDescription(self):
        return "Takes an input parallel corpus and provides the first n lines of each side of the corpus as output."
    def getRequiredPaths(self): return ['mt-analyzers']
    def getParamNames(self): return [ ('nLines', 'the number of lines that should be taken from the head of each side of the parallel corpus') ]

    def getInputNames(self, params):
        return [ ('fCorpusIn', 'foreign side of parallel corpus, one sentence per line'),
                 ('eCorpusIn', '"English" side of parallel corpus, one sentence per line') ]

    def getOutputNames(self, params):
        return [ ('fCorpusOut', 'foreign side of parallel corpus, one sentence per line'),
                 ('eCorpusOut', '"English" side of parallel corpus, one sentence per line') ]
    
    def getCommands(self, params, inputs, outputs):        
        cmd1 = ('head -n %(nLines)s '%params +
               '< %(fCorpusIn)s '%inputs +
               '> %(fCorpusOut)s'%outputs)
        
        cmd2 = ('head -n %(nLines)s '%params +
               '< %(eCorpusIn)s '%inputs +
               '> %(eCorpusOut)s'%outputs)
        
        return [ cmd1, cmd2 ]

    def getPostAnalyzers(self, params, inputs, outputs):
        cmd = ('AnalyzeParCorpus.sh %(fCorpusOut)s %(eCorpusOut)s'%outputs
               )
        return [ cmd ]

if __name__ == '__main__':
    import sys
    t = ParallelHead()
    t.handle(sys.argv)
