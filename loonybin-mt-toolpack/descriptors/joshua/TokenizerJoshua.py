from loonybin import Tool

class TokenizerJoshua(Tool):

    def getName(self):
        return 'Machine Translation/Monolingual Corpus/Tokenizer (Moses)'

    def getDescription(self):
        return ("Takes an input corpus and tokenize it")

    def getRequiredPaths(self):
        return ["moses"]

    def getParamNames(self):
        return [("targetLanguageSuffix", "Two-letter-long suffices specifying the target language. ('en' for English, 'de' for German, and 'el' for Spanish are supported)")]

    def getInputNames(self, params):
        return [("split:inputCorpus", "An input corpus to be tokenized")]

    def getOutputNames(self, params):
        return [("merge:compress:tokenizedCorpus", "The tokenized input corpus")]

    def getPreAnalyzers(self, params, inputs):
        return ['echo InputCorpusWordCount `wc -w %(split:inputCorpus)s`'%(inputs),
		'echo InputCorpusLineCount `wc -l %(split:inputCorpus)s`'%(inputs)]

    def getCommands(self, params, inputs, outputs):
	if params["targetLanguageSuffix"] == '':
	    return ['cat %s | perl ./scripts/tokenizer/tokenizer.perl > %s' % (inputs["split:inputCorpus"], outputs["merge:compress:tokenizedCorpus"])]
	else:
	    return ['cat %s | perl ./scripts/tokenizer/tokenizer.perl -l %s > %s' % (inputs["split:inputCorpus"], params["targetLanguageSuffix"], outputs["merge:compress:tokenizedCorpus"])]

    def getPostAnalyzers(self, params, inputs, outputs):
        return ['echo TokenizedCorpusWordCount `wc -w %(merge:compress:tokenizedCorpus)s`'%(outputs),
		'echo TokenizedCorpusLineCount `wc -l %(merge:compress:tokenizedCorpus)s`'%(outputs)]

if __name__ == '__main__':
    import sys
    t = TokenizerJoshua();
    t.handle(sys.argv)
