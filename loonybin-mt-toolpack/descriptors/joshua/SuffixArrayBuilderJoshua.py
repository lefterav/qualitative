from loonybin import Tool

class SuffixArrayBuilderJoshua(Tool):

    def getName(self):
        return 'Machine Translation/Parallel Corpus/Suffix Array Builder (Joshua)'

    def getDescription(self):
        return ("Takes an input parallel corpus and the alignments data of it and build a suffix array which can be used for grammar extraction.")

    def getRequiredPaths(self):
        return ["joshua-jar"]

    def getParamNames(self):
        return [("JVMOptions", "JVM options. You may specify amount of heap space, e.g., by '-Xmx512m', or specify the 64-bit flag by '-d64', which you might want to accompany with a heap space amount such as '-Xmx10g'")]

    def getInputNames(self, params):
        return [("englishCorpus", "the English side of the parallel corpus"),
	        ("foreignCorpus", "the foreign side of the parallel corpus"),
		("alignmentMap", "a map of the alignments between the two sides of the parallel corpus in the direction of the foreign-English")]

    def getOutputNames(self, params):
        return [("commonSymbolTable", "Common symbol table for source and target language"),
		("foreignBinaryCorpus", "Source language corpus"),
		("foreignSuffixArray", "Source language suffix array"),
		("englishBinaryCorpus", "Target language corpus"),
		("englishSuffixArray", "Target language suffix array"),
		("alignmentGrids", "Source-target alignment grids"),
                ("frequentPhrases", "Frequent phrases produced along with suffix array"),
		("lexprobs", "Lexprobs")]


    def getPreAnalyzers(self, params, inputs):
        return ['echo EnglishCorpusWordCount `wc -w %(englishCorpus)s`'%(inputs),
		"echo EnglishCorpusLineCount `awk 'END {print NR} {if(NF>99){print \"More than 99 tokens at line \"NR; exit 1}}' %(englishCorpus)s`"%(inputs),
	        'echo ForeignCorpusWordCount `wc -w %(foreignCorpus)s`'%(inputs),
		"echo ForeignCorpusLineCount `awk 'END {print NR} {if(NF>99){print \"More than 99 tokens at line \"NR; exit 1}}' %(foreignCorpus)s`"%(inputs),
		'echo AlignmentsWordCount `wc -w %(alignmentMap)s`'%(inputs),
		'echo AlignmentsLineCount `wc -l %(alignmentMap)s`'%(inputs)]

    def getCommands(self, params, inputs, outputs):
        commands = []
        commands.append('java %s -Dfile.encoding=utf8 -cp joshua.jar joshua.corpus.suffix_array.Compile %s %s %s model' % 
		(params["JVMOptions"], inputs["foreignCorpus"], inputs["englishCorpus"], inputs["alignmentMap"]));

        commands.append('dir=`pwd`')
        commands.append('ln -s $dir/model/common.vocab %(commonSymbolTable)s' % (outputs))
        commands.append('ln -s $dir/model/source.corpus %(foreignBinaryCorpus)s' % (outputs))
        commands.append('ln -s $dir/model/source.suffixes %(foreignSuffixArray)s' % (outputs))
        commands.append('ln -s $dir/model/target.corpus %(englishBinaryCorpus)s' % (outputs))
        commands.append('ln -s $dir/model/target.suffixes %(englishSuffixArray)s' % (outputs))
        commands.append('ln -s $dir/model/alignment.grids %(alignmentGrids)s' % (outputs))
        commands.append('ln -s $dir/model/lexprobs.txt %(lexprobs)s' % (outputs))
        commands.append('ln -s $dir/model/frequentPhrases %(frequentPhrases)s' % (outputs))
        return commands

    def getPostAnalyzers(self, params, inputs, outputs):
        return ['echo CommonSymbolTableSize `du -b %(commonSymbolTable)s`'%(outputs),
		'echo ForeignBinaryCorpusSize `du -b %(foreignBinaryCorpus)s`'%(outputs),
		'echo ForeignSuffixArraySize `du -b %(foreignSuffixArray)s`'%(outputs),
		'echo EnglishBinaryCorpusSize `du -b %(englishBinaryCorpus)s`'%(outputs),
		'echo EnglishSuffixArraySize `du -b %(englishSuffixArray)s`'%(outputs),
		'echo AlignmentGridsSize `du -b %(alignmentGrids)s`'%(outputs),
		'echo LexprobsLineCount `wc -l %(lexprobs)s`'%(outputs)]

if __name__ == '__main__':
    import sys
    t = SuffixArrayBuilderJoshua();
    t.handle(sys.argv)
