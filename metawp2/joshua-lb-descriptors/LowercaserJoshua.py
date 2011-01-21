from loonybin import Tool

class LowercaserJoshua(Tool):

    def getName(self):
        return 'Machine Translation/Monolingual Corpus/Lowercaser (Joshua)'

    def getDescription(self):
        return ("Takes an input tokenized corpus and lowercase it")

    def getRequiredPaths(self):
        return ["moses"]

    def getParamNames(self):
        return []

    def getInputNames(self, params):
        return [("tokenizedCorpus", "The tokenized input corpus to be lowercased")]

    def getOutputNames(self, params):
        return [("normalizedCorpus", "The tokenized and lowercased corpus")]

    def getPreAnalyzers(self, params, inputs):
        return ['echo TokenizedCorpusWordCount `wc -w %(tokenizedCorpus)s`'%(inputs),
		'echo TokenizedCorpusLineCount `wc -l %(tokenizedCorpus)s`'%(inputs)]

    def getCommands(self, params, inputs, outputs, paths):
	return ['cat %s | perl %s/scripts/tokenizer/lowercase.perl > %s' % (inputs["tokenizedCorpus"], paths["moses"], outputs["normalizedCorpus"])]

    def getPostAnalyzers(self, params, inputs, outputs):
        return ['echo NormalizedCorpusWordCount `wc -w %(normalizedCorpus)s`'%(outputs),
		'echo NormalizedCorpusLineCount `wc -l %(normalizedCorpus)s`'%(outputs)]

if __name__ == '__main__':
    import sys
    t = LowercaserJoshua();
    t.handle(sys.argv)
