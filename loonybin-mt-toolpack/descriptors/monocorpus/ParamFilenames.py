from loonybin import Tool

class ParamFilename(Tool):
    def getName(self):
        return 'Machine Translation/Monolingual Corpus/Dynamic Filenames'
    
    def getDescription(self):
        return "Allows to enter filenames that include replacement wildcards, allowing for execution of multiple language pairs, whose data are located at the same directory"
    
    
    def getParamNames(self):
        return [ ('corpus', 'corpus file, replacement wildcards allowed'),
                 ('source-language', 'abbreviation used for source language'),
                 ('target-language', 'abbreviation used for source language'),
                 ('language-pair', 'abbreviation used for the language pair') ]
    
    def getInputNames(self, params):
        return [  ]

    def getOutputNames(self, params):
        return [ ('corpus', 'corpus file, replacements done')            ]
    
    def __doReplacements__(self, filename, params):
        filename = filename.replace("$src", params['source-language'])
        filename = filename.replace("$tgt", params['target-language'])
        filename = filename.replace("$pair", params['language-pair'])
        return filename
    
    def getCommands(self, params, inputs, outputs):   
        filename = self.__doReplacements__( params['corpus'], params )
        cmd = ("ln -s %s %s"%(filename, outputs['corpus']) )

        return [ cmd ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [  ]

if __name__ == '__main__':
    import sys
    t = ParamFilename()
    t.handle(sys.argv)
