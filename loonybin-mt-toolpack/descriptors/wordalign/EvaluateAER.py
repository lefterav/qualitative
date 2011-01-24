from loonybin import Tool

class EvaluateAER(Tool):
    
    def getName(self):
        return 'Machine Translation/Word Alignment/Evaluate Word Alignment'
    
    def getDescription(self):
        return "Uses the Alignment Set Toolkit to evaluate the Alignment Error Rate of the word alignment with regard to some gold standard word alignment"
    
    def getRequiredPaths(self):
        return ['alignment-set-toolkit']

    def getParamNames(self):
        return [ ('goldFormat','format of the gold-aligned data (default: NAACL)'),
                 ('autoFormat','format of the automatically aligned data (default: giza)') ]
    
    def getInputNames(self, params):
        return [ ('goldAlignment', 'hand alignments on held-out set'),
                 ('autoAlignment','automatic alignments on held-out set') ]

    def getOutputNames(self, params):
        return [ ('report', 'report of alignment quality') ]
    
    def getCommands(self, params, inputs, outputs):
        return [ 'perl ./bin/evaluate_alSet-1.1.pl -sub %(autoAlignment)s -ans %(goldAlignment)s'%inputs+
                 ' -subf %(autoFormat)s -ansf %(goldFormat)s'%params+
                 ' > %(report)s'%outputs]
        
    def getPostAnalyzers(self, params, inputs, outputs):
        # TODO: Better logging of results
        return [ ]

if __name__ == '__main__':
    import sys
    t = EvaluateAER()
    t.handle(sys.argv)
