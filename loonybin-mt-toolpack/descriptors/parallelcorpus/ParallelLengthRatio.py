from loonybin import Tool

class ParallelLengthRatio(Tool):
    def getName(self):
        return 'Machine Translation/Parallel Corpus/Calculate Length Ratio'
    
    def getDescription(self):
        return "Takes an input parallel corpus and provides the first n lines of each side of the corpus as output."
    
    def getRequiredPaths(self):
        return [ ]
    
    def getInputNames(self, params):
        return [ ('fCorpusIn', 'foreign side of parallel corpus, one sentence per line'),
                 ('eCorpusIn', '"English" side of parallel corpus, one sentence per line') ]

    def getOutputNames(self, params):
        return [ ('ratioTgtOverSrc','a single floating point number') ]
    
    def getCommands(self, params, inputs, outputs):    
        return ['echo "scale=4; `cat %(eCorpusIn)s | wc -l`/`cat %(fCorpusIn)s | wc -l`" | bc -q'%inputs +
                ' > %(ratioTgtOverSrc)s'%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return []

if __name__ == '__main__':
    import sys
    t = ParallelLengthRatio()
    t.handle(sys.argv)
