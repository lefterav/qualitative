from loonybin import Tool

class GenerateAlignment(Tool):
    def getName(self):
        return 'Machine Translation/Parallel Corpus/Generate Monotone Alignment'
    
    def getDescription(self):
        return "For a parallel corpus with THE SAME NUMBER OF TOKENS ON EVERY LINE, produces a monotone alignment"
    
    def getRequiredPaths(self):
        return []
    
    def getInputNames(self, params):
        return [ ('fCorpus','either side of the input corpus'),
                 ('eCorpus','either side of the input corpus') ]

    def getOutputNames(self, params):
        return [ ('alignment', 'alignment in Moses format') ]
    
    def getCommands(self, params, inputs, outputs):        
        return ['awk \'{for (i=1; i<=NF; i++){printf i"-"i" " }printf"\\n"}\' < %(fCorpus)s'%inputs+
                ' > %(alignment)s'%outputs]

    def getPostAnalyzers(self, params, inputs, outputs):
        return []

if __name__ == '__main__':
    import sys
    t = GenerateAlignment()
    t.handle(sys.argv)
