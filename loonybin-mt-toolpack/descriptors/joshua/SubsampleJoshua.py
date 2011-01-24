from loonybin import Tool

class SubsampleJoshua(Tool):

    def getName(self):
        return 'Machine Translation/Parallel Corpus/Subsample (Joshua)'

    def getDescription(self):
        return ("Takes an input parallel corpus and uses Joshua's built-in" +
               " subsampling facility to reduce its size.")

# i will eventually fill in all of these methods
# -- jonny
    def getRequiredPaths(self):
        return [ "joshua", "joshua-jar"]

    def getParamNames(self):
        return [("ratio", "ratio of output foreign length to output English length"),
	        ("heapSizeInMegs", "amount of heap space to allocate for the Java virtual machine, in MB")]

    def getInputNames(self, params):
        return [("englishCorpus", "the English side of the parallel corpus"),
	        ("foreignCorpus", "the foreign side of the parallel corpus"),
		("testData", "the foreign-side test data")]

    def getOutputNames(self, params):
        return [("englishSubsample", "subsampled English side"),
	        ("foreignSubsample", "subsampled foreign side")]

    def getPreAnalyzers(self, params, inputs):
        return ['echo English before subsample: `wc -lw %(englishCorpus)s`'%(inputs),
	        'echo Foreign before subsample: `wc -lw %(foreignCorpus)s`'%(inputs)]

    def getCommands(self, params, inputs, outputs):
        INPUT_BASENAME = "complete"
	OUTPUT_BASENAME = "subsampled"
	ENGLISH_SUFFIX = "en"
	FOREIGN_SUFFIX = "fr"
        commands = []
	commands.append('echo %s > manifest' % INPUT_BASENAME)
	commands.append('ln -s %s %s.%s'%(inputs["englishCorpus"], INPUT_BASENAME, ENGLISH_SUFFIX))
	commands.append('ln -s %s %s.%s'%(inputs["foreignCorpus"], INPUT_BASENAME, FOREIGN_SUFFIX))

	commands.append('java -Xmx%sm -Xincgc -cp joshua.jar:/share/emplus/software/joshua/lib/commons-cli-2.0-SNAPSHOT.jar -Dfile.encoding=utf8 joshua.subsample.Subsampler -e %s -f %s -epath . -fpath . -output %s -ratio %s -test %s -training manifest' %(params["heapSizeInMegs"], ENGLISH_SUFFIX, FOREIGN_SUFFIX, OUTPUT_BASENAME, params["ratio"], inputs["testData"]))

	commands.append('ln -s `pwd`/%s.%s %s' % (OUTPUT_BASENAME, ENGLISH_SUFFIX, outputs["englishSubsample"]))
	commands.append('ln -s `pwd`/%s.%s %s' % (OUTPUT_BASENAME, FOREIGN_SUFFIX, outputs["foreignSubsample"]))
	return commands

    def getPostAnalyzers(self, params, inputs, outputs):
        return ['echo English after subsample: `wc -lw %(englishSubsample)s`'%(outputs),
	        'echo Foreign after subsample: `wc -lw %(foreignSubsample)s`'%(outputs)]

if __name__ == '__main__':
    import sys
    ss = SubsampleJoshua()
    ss.handle(sys.argv)
