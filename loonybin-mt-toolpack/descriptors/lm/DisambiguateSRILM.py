from loonybin import Tool

class DisambiguateSRILM(Tool):
    
    def getName(self):
        return 'Machine Translation/Language Modeling/Disambiguate (SRILM)'
    
    def getDescription(self):
        return "Disambiguates using an ARPA language model using interpolation and modified Knesser-Ney smoothing (more options to come soon) that will include the special UNK token using SRILM"
    
    def getRequiredPaths(self):
        return ['srilm']

    def getParamNames(self):
        return [ ('order','order of the LM'),
                 ('smoothingType','wbdiscount for Witten-Bell smoothin, kndiscount for Modified Knesser-Ney smoothing, or ukndiscount for unmodified Knesser-Ney smoothing'),
                 ('interpolate','Should interpolation with lower-order counts be used when estimating? (true or false)') ]
    
    def getInputNames(self, params):
        return [ ('corpusIn','corpus to be disambiguated, one sentence per line from which the language model will be estimated'),
		 ('arpaLM','ARPA-format n-gram language model'),
		 ('map', 'Map that defines the disambiguation') ]

    def getOutputNames(self, params):
        return [ ('corpusOut', 'disambiguated corpus') ]
    
    def getPreAnalyzers(self, params, inputs):
        return [ 'echo corpusInWordCount `wc -w %(corpusIn)s'%inputs,
		 'echo corpusInLineCount `wc -l %(corpusIn)s'%inputs,
		 'echo arpaLMSize `du -h $(arpaLM)s'%inputs ]
    
    def getCommands(self, params, inputs, outputs):
        interpolation = ''
        if params['interpolate'][0].lower() == 't':
            interpolation = ' -interpolate '
        
        # SRILM machine type doesn't always work.  To minimize inconvenience,
        # link actual subdir to ``i686'', ex:
        # $ ln -s i686-m64 i686
        return [ './bin/i686/disambig -%(smoothingType)s -order %(order)s -keep-unk'%params +
                interpolation +
                ' -text %(corpusIn)s -lm %(arpaLM)s -map %(map)s'%inputs +
                ' > corpusOut',
		'ln -s corpusOut %(corpusOut)s'%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = DisambiguateSRILM()
    t.handle(sys.argv)
