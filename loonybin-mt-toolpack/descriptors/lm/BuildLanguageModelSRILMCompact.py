from loonybin import Tool

class BuildLanguageModel(Tool):
    
    def getName(self):
        return 'Machine Translation/Language Modeling/Build Language Model (SRILM, compact)'
    
    def getDescription(self):
        return "Builds an ARPA language model using SRILM with compact data structures.  Use for large data."
    
    def getRequiredPaths(self):
        return ['srilm-compact']

    def getParamNames(self):
        return [ ('order','order of the LM'),
                 ('smoothingType','wbdiscount for Witten-Bell smoothin, kndiscount for Modified Knesser-Ney smoothing, or ukndiscount for unmodified Knesser-Ney smoothing'),
                 ('interpolate','Should interpolation with lower-order counts be used when estimating? (true or false)') ]
    
    def getInputNames(self, params):
        return [ ('corpusIn','plaintext corpus, one sentence per line from which the language model will be estimated') ]

    def getOutputNames(self, params):
        return [ ('arpaLM','ARPA-format n-gram language model') ]

    def getPreAnalyzers(self, params, inputs):
        return [ 'echo corpusInWordCount `wc -w %(corpusIn)s`'%inputs,
		 'echo corpusInLineCount `wc -l %(corpusIn)s`'%inputs ]
    
    def getCommands(self, params, inputs, outputs):
        interpolation = ''
        if params['interpolate'][0].lower() == 't':
            interpolation = ' -interpolate '
        
        # SRILM machine type doesn't always work.  To minimize inconvenience,
        # link actual subdir to ``i686_c'', ex:
        # $ ln -s i686-m64_c i686_c
        return [ './bin/i686_c/ngram-count -%(smoothingType)s -order %(order)s -unk'%params +
                interpolation +
                ' -text %(corpusIn)s'%inputs +
                ' -lm %(arpaLM)s'%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
	return [ 'echo arpaLMSize `du -h %(arpaLM)s`'%outputs ]

if __name__ == '__main__':
    import sys
    t = BuildLanguageModel()
    t.handle(sys.argv)
