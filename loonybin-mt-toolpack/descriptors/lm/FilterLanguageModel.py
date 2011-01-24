from loonybin import Tool

class Combine(Tool):
    
    def getName(self):
        return 'Machine Translation/Language Modeling/Filter Language Model to Sentences'
    
    def getDescription(self):
        return "Filters an ARPA format language model to an input set, given the n-grams from that set."
    
    def getRequiredPaths(self):
        return ['lm-filter']

    def getParamNames(self):
        return [ ]
    
    def getInputNames(self, params):
        return [ ('lmIn','ARPA format langauge model'),
                 ('tgtVocab','target unigram vocabulary for the desired input set')]

    def getOutputNames(self, params):
        return [ ('lmOut','filtered language model') ]
    
    def getCommands(self, params, inputs, outputs):
        return [ 'cat %(tgtVocab)s | ./filter union %(lmIn)s'%inputs +
                  ' %(lmOut)s'%outputs]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = Combine()
    t.handle(sys.argv)
