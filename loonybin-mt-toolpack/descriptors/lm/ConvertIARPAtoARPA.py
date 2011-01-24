from loonybin import Tool

class Convert(Tool):
    
    def getName(self):
        return 'Machine Translation/Language Modeling/Convert iARPA to ARPA (IRSTLM)'
    
    def getDescription(self):
        return "Converts an IRSTLM iARPA file to ARPA format"
    
    def getRequiredPaths(self):
        return ['irstlm']

    def getParamNames(self):
        return [ ]
    
    def getInputNames(self, params):
        return [ ('iArpaGz','gzipped iARPA file') ]

    def getOutputNames(self, params):
        return [ ('arpaLM','ARPA format language model') ]

    def getPreAnalyzers(self, params, inputs):
        return [ ]
    
    def getCommands(self, params, inputs, outputs):
        return [ 'export IRSTLM=.',
                 '# Use .gz extention so IRSTLM knows what format to read',
                 'ln -s %s lm.gz'%inputs['iArpaGz'],
                 './bin/compile-lm lm.gz --text yes %s'%(outputs['arpaLM']) ]

    def getPostAnalyzers(self, params, inputs, outputs):
	return [ ]

if __name__ == '__main__':
    import sys
    t = Convert()
    t.handle(sys.argv)
