from loonybin import Tool

class Parse(Tool):
    
    def getName(self):
        return 'Machine Translation/Parsing/Stanford English Parser'
    
    def getDescription(self):
        return """
        Option to use SAMT to parse in parallel?
        """
    
    def getRequiredPaths(self):
        return ['stanford-en-parser']

    def getParamNames(self):
        return [ ('nNodes','Number of nodes to use on the cluster'),
                 ('nReducers','How many reducers should the cluster use? (More=lose less sentences/slower)')]

    def getInputNames(self, params):
        return [ ('eCorpusIn', 'English side of parallel corpus, one sentence per line')]

    def getOutputNames(self, params):
        return [ ('eParsesOut', '"English" side of parallel corpus parsed, one sentence per line; failed parses will not start with a paren') ]
    
    def getCommands(self, params, inputs, outputs):
        return [ ( '`gen_test_parses_stanford.sh paramfile.params filetoparse parser phasename`'%inputs +
                   ' %(eParsesOut)s '%outputs +
                   ' %(nNodes)s %(nReducers)s'%params) ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = Parse()
    t.handle(sys.argv)
