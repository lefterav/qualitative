from loonybin import Tool

class MakeWordClasses(Tool):
    
    def getName(self):
        return 'Machine Translation/Word Alignment/MGIZA Local/Make Word Classes'
    
    def getDescription(self):
        return "Performs unsupervised word class clustering to support the X model"
    
    def getRequiredPaths(self):
        return ['mgiza', 'mt-analyzers']

    def getParamNames(self):
        return [ ('numClasses', 'number of word classes to induce (Moses default: 50)'),
                 ('numOptimizationRuns','number of optimization runs. More leads to better quality, but slower performance (Moses default: 2)')]

    def getInputNames(self, params):
        return [ ('corpusIn','raw text input for one side of the parallel corpus') ]

    def getOutputNames(self, params):
        return [ ('classesOut','file to write class data to') ]
    
    def getCommands(self, params, inputs, outputs):
        return [ ('./src/mkcls/mkcls -c%(numClasses)s -n%(numOptimizationRuns)s '%params + 
                  '-p%(corpusIn)s '%inputs + 
                  '-V%(classesOut)s opt'%outputs) ] 

    ### TODO: Write postanalyzer that gives some samples from the various classes

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = MakeWordClasses()
    t.handle(sys.argv)
