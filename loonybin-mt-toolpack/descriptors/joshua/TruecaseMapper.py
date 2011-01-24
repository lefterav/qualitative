from loonybin import Tool

class TruecaseMapper(Tool):

    def getName(self):
        return 'Machine Translation/Monolingual Corpus/Build Truecase Map (Joshua)'

    def getDescription(self):
        return ("Takes an plaintext corpus and build a truecase map based on it. The corpus should be truecased and tokenized to work correctly.")

    def getRequiredPaths(self):
        return ["joshua-scripts"]

    def getParamNames(self):
        return []

    def getInputNames(self, params):
        return [("inputCorpus", "An input corpus from which a truecase map will be built")]

    def getOutputNames(self, params):
        return [("truecaseMap", "The truecase map to be built based on inputCorpus")]

    def getPreAnalyzers(self, params, inputs):
        return ['echo InputCorpusWordCount `wc -w %(inputCorpus)s`'%(inputs),
		'echo InputCorpusLineCount `wc -l %(inputCorpus)s`'%(inputs)]

    def getCommands(self, params, inputs, outputs):
	return ['cat %(inputCorpus)s | '%inputs +
		'perl ./truecase-map.perl > %(truecaseMap)s'%outputs]

    def getPostAnalyzers(self, params, inputs, outputs):
        return ['echo TruecaseMapLineCount `wc -l %(truecaseMap)s`'%outputs]

if __name__ == '__main__':
    import sys
    t = TruecaseMapper();
    t.handle(sys.argv)
