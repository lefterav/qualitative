from loonybin import Tool

class DetokenizerJoshua(Tool):

    def getName(self):
        return 'Machine Translation/Monolingual Corpus/Detokenizer (Moses)'

    def getDescription(self):
        return ("Takes an recased and tokenized output of an MT system and detokenize it.")

    def getRequiredPaths(self):
        return ["moses"]

    def getParamNames(self):
        return [("targetLanguageSuffix", "Two-letter-long suffices specifying the target language. For example, 'en' for English, and 'fr' for French.")]

    def getInputNames(self, params):
        return [("recasedOutput", "A recased output of an MT system.")]

    def getOutputNames(self, params):
        return [("detokenizedOutput", "The detokenized output of the input")]

    def getPreAnalyzers(self, params, inputs):
        return ['echo RecasedOutputWordCount `wc -w %(recasedOutput)s`'%(inputs),
		'echo RecasedOutputLineCount `wc -l %(recasedOutput)s`'%(inputs)]

    def getCommands(self, params, inputs, outputs, paths):
	if params["targetLanguageSuffix"] == '':
	    return [ 'cat %s | perl %s/scripts/tokenizer/detokenizer.perl > %s' % (inputs["recasedOutput"], paths["moses"], outputs["detokenizedOutput"]) ]
	else:
	    return [ 'cat %s | perl %s/scripts/tokenizer/detokenizer.perl -l %s > %s' % (inputs["recasedOutput"], paths["moses"], params["targetLanguageSuffix"], outputs["detokenizedOutput"]) ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return ['echo DetokenizedOutputWordCount `wc -w %(detokenizedOutput)s`'%(outputs),
		'echo DetokenizedOutputLineCount `wc -l %(detokenizedOutput)s`'%(outputs)]

if __name__ == '__main__':
    import sys
    t = DetokenizerJoshua();
    t.handle(sys.argv)
