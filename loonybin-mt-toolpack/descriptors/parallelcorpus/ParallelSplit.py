from loonybin import Tool

class ParallelHead(Tool):
    def getName(self):
        return 'Machine Translation/Parallel Corpus/Split'
    
    def getDescription(self):
        return "Takes an input parallel corpus and provides the first n lines of each side of the corpus as output."
    
    def getRequiredPaths(self):
        return []
    
    def getParamNames(self):
        return [ ('nHeadLines', 'number of lines to be taken from the head of the parallel corpus') ]

    def getInputNames(self, params):
        return [ ('fCorpus', 'foreign side of parallel corpus, one sentence per line'),
                 ('eCorpus', '"English" side of parallel corpus, one sentence per line') ]

    def getOutputNames(self, params):
        return [ ('fHead', 'foreign side of parallel corpus, one sentence per line'),
                 ('eHead', '"English" side of parallel corpus, one sentence per line'),
                 ('fTail', 'foreign side of parallel corpus, one sentence per line'),
                 ('eTail', '"English" side of parallel corpus, one sentence per line') ]

        
    def getPreAnalyzers(self, params, inputs):
        #TODO: this line underneath doesn't work. Do sth to captur the case when nHeadLines is bigger than the corpus size
        cmd = "if [ $( wc -l < %s ) -lt %s ] ; then echo \"Number of lines to be split is bigger than the original file. Please check your split settings\"; exit 1 ; fi"%(inputs['eCorpus'], params['nHeadLines'])
        return [cmd]


    def getCommands(self, params, inputs, outputs):
        cmd1 = ('head -n %(nHeadLines)s '%params +
               '< %(fCorpus)s '%inputs +
               '> %(fHead)s'%outputs)
        
        cmd2 = ('tail -n +%(nHeadLines)s '%params +
               '< %(fCorpus)s '%inputs +
               '> %(fTail)s'%outputs)
        
        cmd3 = ('head -n %(nHeadLines)s '%params +
               '< %(eCorpus)s '%inputs +
               '> %(eHead)s'%outputs)
        
        cmd4 = ('tail -n +%(nHeadLines)s '%params +
               '< %(eCorpus)s '%inputs +
               '> %(eTail)s'%outputs)
        
        return [ cmd1, cmd2, cmd3, cmd4 ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]



if __name__ == '__main__':
    import sys
    t = ParallelHead()
    t.handle(sys.argv)
