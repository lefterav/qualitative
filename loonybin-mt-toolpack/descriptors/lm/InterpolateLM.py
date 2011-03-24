from loonybin import Tool

class InterpolateLM(Tool):

    def getName(self):
        return 'Machine Translation/Language Modeling/Interpolate LM (Moses, SRILM)'

    def getDescription(self):
        return ("If you decide to use multiple corpora for the language model, you may also want to try out interpolating the individual language models (instead of using them as separate feature functions) ")

    def getRequiredPaths(self):
        return ["moses-scripts", "srilm"]

    def getParamNames(self):
        return [ ('number-of-LMs','number of language models to interpolate') ] 

    def getInputNames(self, params):
        inputs = []
        numFiles = 1
        try:
            numFiles = int(params['number-of-LMs'])
        except ValueError:
            numFiles = 2
        for i in xrange(1, numFiles+1):
            inputs.append( ("lm%d" %i , "Language model to be used for interpolation") )
        inputs.append(("fTuningCorpus", "A target-language corpus used for estimating the weights for interpolating language models"))
        return inputs 
    

    def getOutputNames(self, params):
        return [("interpolated-lm", "Language model resulting from the interpolation process")]


    def getCommands(self, params, inputs, outputs, paths):
        try:
            numFiles = int(params['number-of-LMs'])
        except ValueError:
            numFiles = 2
        lms = []
        for i in xrange(1, numFiles+1):
            lms.append(inputs["lm%d" % i]) 
        lmfiles = ','.join(lms)          
        return ['perl ./ems/support/interpolate-lm.perl --tuning %s --name %s  --srilm %s/bin/i686 --lm %s ' % (inputs["fTuningCorpus"], outputs["interpolated-lm"], paths["srilm"], lmfiles)]



if __name__ == '__main__':
    import sys
    t = InterpolateLM();
    t.handle(sys.argv)
