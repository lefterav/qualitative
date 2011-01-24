from loonybin import Tool

class BerkeleyAligner(Tool):

    def getName(self):
        return 'Machine Translation/Word Alignment/Berkeley Unsupervised Aligner'

    def getDescription(self):
        return ("Takes an input parallel corpus and uses the Berkeley" +
               " Aligner to compute word alignments.")

    def getRequiredPaths(self):
        return ["berkeley-unsupervised-aligner"]

    def getParamNames(self):
        return [("heapSizeInMegs", "amount of memory to be allocated to the JVM, in megabytes"),
	        ("otherJVMOptions", "other arguments to the JVM"),
	        ("base_name", "base name of the output alignments"),
		("numThreads", "number of parallel threads of execution"),
                ("iterations", "number of EM iterations")]

    def getInputNames(self, params):
        return [("englishCorpus", "the English side of the parallel corpus"),
	        ("foreignCorpus", "the foreign side of the parallel corpus")]

    def getOutputNames(self, params):
        return [("alignmentMap", "a map of the alignments between the two sides of the parallel corpus")]

    def getPreAnalyzers(self, params, inputs):
        return ['echo EnglishCorpusWordCount `wc -w %(englishCorpus)s`'%(inputs),
                "echo EnglishCorpusLineCount `wc -l %(englishCorpus)s`"%(inputs),
                'echo ForeignCorpusWordCount `wc -w %(foreignCorpus)s`'%(inputs),
                "echo ForeignCorpusLineCount `wc -l %(foreignCorpus)s`"%(inputs)]

    def getCommands(self, params, inputs, outputs):
		ENGLISH_SUFFIX = "en"
		FOREIGN_SUFFIX = "fr"
		BASE_NAME = params["base_name"]
                CORPUS_DIR = "traincorpus"
		EXEC_DIR = "alignments"
		CONF_FILE = "wordalign.conf"
		cmd = []
                cmd.append("mkdir -p %s" % CORPUS_DIR)
		cmd.append("ln -s ../%s %s/%s.%s" % (inputs["englishCorpus"], CORPUS_DIR, BASE_NAME, ENGLISH_SUFFIX))
		cmd.append("ln -s ../%s %s/%s.%s" % (inputs["foreignCorpus"], CORPUS_DIR, BASE_NAME, FOREIGN_SUFFIX))
		conf = []
		conf.append(("trainSources", "./%s/" % CORPUS_DIR))
		conf.append(("execDir", EXEC_DIR))
		conf.append(("numThreads", params["numThreads"]))
		conf.append(("forwardModels", "MODEL1"))
		conf.append(("reverseModels", "MODEL1"))
		conf.append(("mode", "JOINT"))
		conf.append(("iters",  params["iterations"]))
		conf.append(("create", ""))
		conf.append(("saveParams", "false"))
		conf.append(("msPerLine", "10000"))
		conf.append(("alignTraining", ""))
		conf.append(("foreignSuffix", FOREIGN_SUFFIX))
		conf.append(("englishSuffix", ENGLISH_SUFFIX))
		conf.append(("sentences", "MAX"))
		conf.append(("competitiveThresholding", ""))
		for (p,x) in conf:
			cmd.append("echo '%s %s' >>%s" % (p, x, CONF_FILE))
		cmd.append("mkdir -p example/test");
		cmd.append("java -Xmx%sm %s -jar berkeleyaligner.jar ++%s" % (params["heapSizeInMegs"], params["otherJVMOptions"], CONF_FILE))
                cmd.append('dir=`pwd`')
		cmd.append("ln -s $dir/%s/%s.%s-%s.align %s" % (EXEC_DIR, BASE_NAME, ENGLISH_SUFFIX, FOREIGN_SUFFIX, outputs["alignmentMap"]))
		return cmd

    def getPostAnalyzers(self, params, inputs, outputs):
        return ['echo AlignmentsWordCount `wc -w %(alignmentMap)s`'%(outputs),
                'echo AlignmentsLineCount `wc -l %(alignmentMap)s`'%(outputs)]

if __name__ == '__main__':
    import sys
    b = BerkeleyAligner()
    b.handle(sys.argv)
