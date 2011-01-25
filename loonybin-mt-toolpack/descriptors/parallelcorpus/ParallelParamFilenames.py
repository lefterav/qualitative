from loonybin import Tool

class ParallelParamFilenames(Tool):
    def getName(self):
        return 'Machine Translation/Parallel Corpus/Dynamic Filenames'
    
    def getDescription(self):
        return "Allows to enter filenames that include replacement wildcards, allowing for execution of multiple language pairs, whose data are located at the same directory"
    
    
    def getParamNames(self):
        return [ ('corpus.f', 'source side of parallel corpus, replacement wildcards allowed'),
                 ('corpus.e', 'target side of parallel corpus,  replacement wildcards allowed'),
                 ('sourceLanguage', 'abbreviation used for source language'),
                 ('targetLanguage', 'abbreviation used for source language'),
                 ('langPair', 'abbreviation used for the language pair') ]
    
    def getInputNames(self, params):
        return [  ]

    def getOutputNames(self, params):
        return [ ('corpus.f', 'source side of parallel corpus, replacements done'),
                 ('corpus.e', 'target side of parallel corpus, replacements done') ]
    
    def __doReplacements__(self, filename, params):
        filename = filename.replace("$src", params['sourceLanguage'])
        filename = filename.replace("$tgt", params['targetLanguage'])
        filename = filename.replace("$pair", params['langPair'])
        return filename
    
    def getCommands(self, params, inputs, outputs):   
        filename = self.__doReplacements__( params['corpus.f'], params )
        cmd1 = ("ln -s %s %s"%(filename, outputs['corpus.f']) )
        
        filename = self.__doReplacements__( params['corpus.e'], params  )
        cmd2 = ("ln -s %s %s"%(filename, outputs['corpus.e']) )
        
        return [ cmd1, cmd2 ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [  ]

if __name__ == '__main__':
    import sys
    t = ParallelParamFilenames()
    t.handle(sys.argv)
