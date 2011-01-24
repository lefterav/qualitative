from loonybin import Tool

class BuildLanguageModel(Tool):
    
    def getName(self):
        return 'Machine Translation/Language Modeling/Build Language Model (IRSTLM)'
    
    def getDescription(self):
        return "Builds an ARPA language model using IRSTLM"
    
    def getRequiredPaths(self):
        return ['irstlm']

    def getParamNames(self):
        return [ ('order','order of the LM'),
                 ('smoothingType','witten-bell for Witten-Bell smoothin, improved-knesser-ney for Modified Knesser-Ney smoothing, or knesser-ney for unmodified Knesser-Ney smoothing'),
                 ('splitParts','number of pieces to split training into') ]
    
    def getInputNames(self, params):
        return [ ('corpus','plaintext corpus, one sentence per line from which the language model will be estimated') ]

    def getOutputNames(self, params):
        return [ ('iArpaGz','Gzipped iARPA-format (not ARPA!) n-gram language model') ]

    def getPreAnalyzers(self, params, inputs):
        return [ ]
    
    def getCommands(self, params, inputs, outputs):
        return [ 'export IRSTLM=.',
                 './bin/build-lm.sh -i "./bin/add-start-end.sh < %(corpus)s"'%inputs +
                 ' -n %(order)s -s %(smoothingType)s -k %(splitParts)s -v '%params +
                 ' -o iArpa',
                 'mv iArpa.gz %(iArpaGz)s'%outputs]

    def getPostAnalyzers(self, params, inputs, outputs):
	return [ ]

if __name__ == '__main__':
    import sys
    t = BuildLanguageModel()
    t.handle(sys.argv)
