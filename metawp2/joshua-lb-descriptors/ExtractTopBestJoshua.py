from loonybin import Tool

class ExtractTopbest(Tool):
    
    def getName(self):
        return 'Machine Translation/Output/Extract Top Best'
    
    def getDescription(self):
        return "Extracts the top-best hypotheses from a Joshua or Moses n-best list."
    
    def getRequiredPaths(self):
        return []

    def getParamNames(self):
        return [ ]
    
    def getInputNames(self, params):
        return [ ('nbestIn','Joshua-format or Moses-format n-best list') ]

    def getOutputNames(self, params):
        return [ ('topbestOut', 'top-best hypotheses, one per line') ]
    
    def getCommands(self, params, inputs, outputs):
        return [ (r"awk -F' \\|\\|\\| ' 'BEGIN{n=-1} {if(n!=$1){print $2;n=$1}}' < %(nbestIn)s"%inputs +
                  " > %(topbestOut)s"%outputs) ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = ExtractTopbest()
    t.handle(sys.argv)
