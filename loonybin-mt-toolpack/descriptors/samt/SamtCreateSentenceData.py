from loonybin import Tool

class SamtPrepareSourceAndRefs(Tool):
    
    def getName(self):
        return 'Machine Translation/SAMT/Create Sentence Data'
    
    def getDescription(self):
        return """
        Formats input training data for building a SAMT system.
        """
    
    def getRequiredPaths(self):
        return ['samt']

    def getParamNames(self):
        # TODO: Add preprocessing option here?
        return [ ('hierMode','?') ]
    
    def getInputNames(self, params):
        inputs = []
        hierMode = Tool.isTrue(self, params['hierMode'])
        if not hierMode:
            inputs.append( ('parses','parses for target corpus') )
        inputs.extend([
                ('hdfs:fCorpus','source corpus'),
                ('hdfs:eCorpus','target corpus'),
                ('hdfs:alignment','symmetrized word alignment')
                ])
        return inputs

    def getOutputNames(self, params):
        return [ ('hdfs:combinedCorpus','Combined dev and ref sentences in SAMT format') ]
    
    def getCommands(self, params, inputs, outputs):
        hierMode = Tool.isTrue(self, params['hierMode'])
        cmd = ''
        if not hierMode:
            cmd += "cat %(parses)s | perl -p -e 's/\(/ \( /g; s/\)/ \) /g; s/\s+/ /g; s/^\s+//g; s/ +$/\n/g;' | "%inputs
        cmd += './m45scripts/zpaste.pl --sbmtpreprocess -s "#" hdfs:%(hdfs:fCorpus)s  hdfs:%(hdfs:eCorpus)s  hdfs:%(hdfs:alignment)s'%inputs
        if not hierMode:
            cmd += ' - '
        cmd += '| ./m45scripts/drop_empty_sentences.pl '
        cmd += '| nl -ba -w1 '
        cmd += '| hadoop dfs -put - %(hdfs:combinedCorpus)s'%outputs
        return [ cmd ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = SamtPrepareSourceAndRefs()
    t.handle(sys.argv)
