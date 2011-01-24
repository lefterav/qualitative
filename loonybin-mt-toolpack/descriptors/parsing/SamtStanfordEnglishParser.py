from loonybin import Tool
from SAMT import SAMT

class Parse(Tool):
    
    def __init__(self):
        self.samt = SAMT()
    
    def getName(self):
        return 'Machine Translation/Parsing/Stanford English Parser (Using SAMT)'
    
    def getDescription(self):
        return """
        Option to use SAMT to parse in parallel?
        """
    
    def getRequiredPaths(self):
        return ['samt']

    def getParamNames(self):
        return [ ]

    def getInputNames(self, params):
        return [ ('eCorpusIn', 'English side of parallel corpus, one sentence per line')]

    def getOutputNames(self, params):
        return [ ('eParsesOut', '"English" side of parallel corpus parsed, one sentence per line; failed parses will not start with a paren') ]
    
    def getCommands(self, params, inputs, outputs):
        samt.makeConfigFile('paramfile.params')
        return ['`gen_test_parses_stanford.sh  paramfile.params %(eCorpusIn)s parser MakeEnglishParses`'%inputs +
                   ' %(eParsesOut)s '%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = Parse()
    t.handle(sys.argv)
