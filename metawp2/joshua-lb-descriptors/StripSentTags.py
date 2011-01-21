from loonybin import Tool

class StripSentTags(Tool):

    def getName(self):
        return 'Machine Translation/Monolingual Corpus/Strip Sent Tags (Joshua)'

    def getDescription(self):
        return ("Takes a corpus which has one sentence per line with sentence tags around each. Mostly used to take off the tags from the corpus out of SRILM disambuator")

    def getRequiredPaths(self):
        return ["joshua-scripts"]

    def getParamNames(self):
        return []

    def getInputNames(self, params):
        return [("corpusIn", "An input corpus from which sent tags will be removed")]

    def getOutputNames(self, params):
        return [("corpusOut", "The output corpus that sent tags are removed")]

    def getPreAnalyzers(self, params, inputs):
        return ['echo CorpusInWordCount `wc -w %(corpusIn)s`'%(inputs),
		'echo CorpusInLineCount `wc -l %(corpusIn)s`'%(inputs)]

    def getCommands(self, params, inputs, outputs):
	return ['cat %(corpusIn)s | '%inputs +
		'perl ./strip-sent-tags.perl > %(corpusOut)s'%outputs]

    def getPostAnalyzers(self, params, inputs, outputs):
        return ['echo CorpusOutWordCount `wc -w %(corpusOut)s`'%(outputs),
		'echo CorpusOutLineCount `wc -l %(corpusOut)s`'%(outputs)]

if __name__ == '__main__':
    import sys
    t = StripSentTags();
    t.handle(sys.argv)
