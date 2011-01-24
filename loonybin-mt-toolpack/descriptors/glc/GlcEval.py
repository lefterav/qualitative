from loonybin import Tool

class GlcEval(Tool):
    
    def getName(self):
        return 'Machine Translation/Global Lexical Coherence/CRF Eval'
    
    def getDescription(self):
        return "Takes a GLC CRF model, source language input sentences, a cdec-format k-best list, and adds an additional feature by running the model in the "
    
    def getRequiredPaths(self):
        return ['glc']

    def getParamNames(self):
        return []

    def getInputNames(self, params):
        inputs = []
        inputs.append( ('mtSourceSents', 'Plaintext sentences used as input to the MT decoder (will be used as target langauge of the GLC model)') )
	inputs.append( ('kbest', 'cdec-format k-best list (will be used as source langauge of the GLC model)') )
	inputs.append( ('cdecWeights', 'cdec-format tuned weights file from decoding') )
        inputs.append( ('glcSrcVocab','Source vocab recognized by GLC feature (source = MT hypothesis language)') )
        inputs.append( ('glcTgtVocab','Target vocab recognized by GLC feature (target = MT input language)') )
        inputs.append( ('glcSrcStopwords','Source stopword list for GLC (source = MT hypothesis language)') )
        inputs.append( ('glcTgtStopwords','Target stopword list for GLC (target = MT input language)') )
        inputs.append( ('glcTTable', 'Translation table (probably a model 1 initialization) for GLC') )
        inputs.append( ('glcFeatWeights','Feature weights for GLC') )
        return inputs

    def getOutputNames(self, params):
        return [ ('rescoredKbest', 'cdec-format k-best list with an additional reverse CRF feature'),
		 ('cdecWeights', 'cdec-format weights file with additional untuned weight for the added feature') ]
    
def getCommands(self, params, inputs, outputs):
        commands = []
        commands.append('./scripts/rescore_preproc.py %(mtSourceSents)s %(kbest)s > glc.cdecCorpus'%inputs)
        commands.append('./glc --eval --useWordPairFeats --useTgtWordFeats --useWordTripletFeats --weightsFile %(glcFeatWeights)s --srcVocabFile %(glcSrcVocab)s --tgtVocabFile %(glcTgtVocab)s --ttFile %(glcTTable)s --srcStopwordFile %(glcSrcStopwords)s --tgtStopwordFile %(glcTgtStopwords)s > glc.logProbs')
        commands.append('./scripts/rescore_postproc.py %s glc.logProbs > %s'%(inputs['kbest'], outputs['rescoredKbest']))
        commands.append('cp %s %s'%(inputs['cdecWeights'], outputs['cdecWeights']))
        commands.append('echo "GlcCrfRev 0.0" >> %s'%(outputs['cdecWeights']))
        return commands

def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = GlcEval()
    t.handle(sys.argv)
