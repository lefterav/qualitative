from loonybin import Tool
import sys

class Chaski(Tool):

    def getName(self):
        return 'Machine Translation/Grammars and Tables/Chaski (Hadoop)/Postprocess Word Alignment'
    
    def getDescription(self):
        return "Run parallel word alignment"
    
    def getRequiredPaths(self):
        return []

    def getParamNames(self):
		return []
    
    def getInputNames(self, params):
        return [ ('mergedAlignments', 'Chaski-format merged alignments')  ]

    def getOutputNames(self, params):
        return [ ('mosesAlignments', 'Moses-format Viterbi alignments') ]
    
    def getCommands(self, params, inputs, outputs):
		return [ "cat %(mergedAlignments)s "%inputs+
				" | awk -F' {##} ' '{print $3}' > %(mosesAlignments)s"%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = Chaski()
    t.handle(sys.argv)
