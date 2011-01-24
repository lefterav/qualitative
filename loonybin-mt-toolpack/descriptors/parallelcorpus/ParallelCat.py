from loonybin import Tool

class ParallelCat(Tool):
    def getName(self):
        return 'Machine Translation/Parallel Corpus/Concatenate'
    
    def getDescription(self):
        return "Takes 2 input parallel corpora and produces a single concatenated parallel corpus (with each side of the parallel corpus still separate)"
    
    def getRequiredPaths(self):
        return ['mt-analyzers']
    
    def getInputNames(self, params):
        return [ ('fCorpus1', 'foreign side of parallel corpus, one sentence per line'),
                 ('eCorpus1', '"English" side of parallel corpus, one sentence per line'),
                 ('fCorpus2', 'foreign side of parallel corpus, one sentence per line'),
                 ('eCorpus2', '"English" side of parallel corpus, one sentence per line') ]

    def getOutputNames(self, params):
        return [ ('fCorpusOut', 'foreign side of parallel corpus, one sentence per line'),
                 ('eCorpusOut', '"English" side of parallel corpus, one sentence per line') ]
    
    def getCommands(self, params, inputs, outputs):        
        cmd1 = ('cat %(fCorpus1)s %(fCorpus2)s'%inputs +
               '> %(fCorpusOut)s'%outputs)
        
        cmd2 = ('cat %(eCorpus1)s %(eCorpus2)s'%inputs +
               '> %(eCorpusOut)s'%outputs)
        
        return [ cmd1, cmd2 ]

    def getPostAnalyzers(self, params, inputs, outputs):
        cmd = ('AnalyzeParCorpus.sh %(fCorpusOut)s %(eCorpusOut)s'%outputs
               )
        return [ cmd ]

if __name__ == '__main__':
    import sys
    t = ParallelCat()
    t.handle(sys.argv)
