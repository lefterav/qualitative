from loonybin import Tool

class GrammarExtractorJoshua(Tool):

    def getName(self):
        return 'Machine Translation/Grammars and Tables/Grammar Extractor (Joshua)'

    def getDescription(self):
        return ("Takes an input parallel corpus and the alignments data of it and build a suffix array which can be used for grammar extraction.")

    def getRequiredPaths(self):
        return ["joshua-jar"]

    def getParamNames(self):
        return [("JVMOptions", "JVM options. You may specify amount of heap space, e.g., by '-Xmx512m', or specify the 64-bit flag by '-d64', which you might want to accompany with a heap space amount such as '-Xmx10g'")]

    def getInputNames(self, params):
        return [("commonSymbolTable", "Common symbol table for source and target language"),
		("foreignBinaryCorpus", "Source language corpus"),
		("foreignSuffixArray", "Source language suffix array"),
		("englishBinaryCorpus", "Target language corpus"),
		("englishSuffixArray", "Target language suffix array"),
        ("frequentPhrases", "Frequent phrases produced along with suffix array"),
		("alignmentGrids", "Source-target alignment grids"),
        ("fDevSents", "Grammar will be extracted so that these sentences can be decoded"),

		("lexprobs", "Lexprobs")]

    def getOutputNames(self, params):
        return [("englishGrammar", "the grammar for the English side")]

    def getPreAnalyzers(self, params, inputs):
        return ['echo CommonSymbolTableSize `du -b %(commonSymbolTable)s`'%(inputs),
		'echo ForeignBinaryCorpusSize `du -b %(foreignBinaryCorpus)s`'%(inputs),
		'echo ForeignSuffixArraySize `du -b %(foreignSuffixArray)s`'%(inputs),
		'echo EnglishBinaryCorpusSize `du -b %(englishBinaryCorpus)s`'%(inputs),
		'echo EnglishSuffixArraySize `du -b %(englishSuffixArray)s`'%(inputs),
		'echo AlignmentGridsSize `du -b %(alignmentGrids)s`'%(inputs),
		'echo LexprobsLineCount `wc -l %(lexprobs)s`'%(inputs)]

    def getCommands(self, params, inputs, outputs):
        commands = []
	commands.append('mkdir -p model')
        commands.append('dir=`pwd`')
        commands.append('ln -s $dir/%(commonSymbolTable)s model/common.vocab' % (inputs))
        commands.append('ln -s $dir/%(foreignBinaryCorpus)s model/source.corpus' % (inputs))
        commands.append('ln -s $dir/%(foreignSuffixArray)s model/source.suffixes' % (inputs))
        commands.append('ln -s $dir/%(englishBinaryCorpus)s model/target.corpus' % (inputs))
        commands.append('ln -s $dir/%(englishSuffixArray)s model/target.suffixes' % (inputs))
        commands.append('ln -s $dir/%(alignmentGrids)s model/alignment.grids' % (inputs))
        commands.append('ln -s $dir/%(lexprobs)s model/lexprobs.txt' % (inputs))
        commands.append('ln -s $dir/%(frequentPhrases)s model/frequentPhrases' % (inputs))
        commands.append('ln -s $dir/%(fDevSents)s model/fDevSents' % (inputs))
        commands.append('java %(JVMOptions)s -Dfile.encoding=utf8 -cp joshua.jar joshua.prefix_tree.ExtractRules model englishCorpus.grammar.raw model/fDevSents' % (params));
        commands.append('sort -u englishCorpus.grammar.raw -o englishCorpus.grammar')
        commands.append('ln -s $dir/englishCorpus.grammar %(englishGrammar)s' % (outputs))
        return commands

    def getPostAnalyzers(self, params, inputs, outputs):
        return ['echo EnglishGrammarWordCount `wc -w %(englishGrammar)s`'%(outputs),
		'echo EnglishGrammarLineCount `wc -l %(englishGrammar)s`'%(outputs)]

if __name__ == '__main__':
    import sys
    t = GrammarExtractorJoshua();
    t.handle(sys.argv)
