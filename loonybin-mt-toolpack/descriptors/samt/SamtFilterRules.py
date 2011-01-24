from loonybin import Tool
from HadoopTool import HadoopTool

class SamtFilterRules(Tool):
    
    def __init__(self):
        self.hadoop = HadoopTool()
    
    def getName(self):
        return 'Machine Translation/SAMT/Filter Rules and add Instance Features'
    
    def getDescription(self):
        return """
        Filters rules to a particular test set and adds instance features (features that need only local rule information to be calculated)
        """
    
    def getRequiredPaths(self):
        return ['samt']

    def getParamNames(self):
        params = self.hadoop.getSharedParams(False)
        
        # Subsample params
        params.extend([
                        ('bufferSize','buffer size for filtering (default: 10000000)')
                        ])
        
        # Filter params
        params.extend([
                        ('maxSourceLength','?'),
                        ('NullRules','?'),
                        ('UseNULL','?'),
                        ('UseRefinedIBM1ProbEstimate','?'),
                        ('noAllowAbstractRules','?'),
                        ('noAllowRulesWithOnlyTargetTerminals','?'),
                        ('lexicalWeightCutoff','? (default: 0.015)'),
                        ('phraseFeatureCount','? (default: 0)'),
                        ('cacheSize','? (default: 4000)'),
                        ('beamFactorLexicalRules','? (default: 0)'),
                        ('beamFactorNonLexicalRules','? (default: 0)'),
                        ('minOccurrenceCountLexicalRules','? (default: 0)'),
                        ('minOccurrenceCountNonlexicalRules','? (default: 0)'),
                        ])
        return params
    
    def getInputNames(self, params):
        return [ ('hdfs:unfilteredRules','?'),
                 ('fFilterSet','Set for which matching rules will be kept in plaintext format, one sentence per line'),
                 ('lexPsgt','lexicon file with lines E F Pr(E|F) called lex.f2n by Moses -- P(S|T)'),
                 ('lexPtgs','lexicon file with lines F E Pr(F|E) called lex.n2f by Moses -- P(T|S)'),
                 ('meanTargetSourceRatio','?') ]

    def getOutputNames(self, params):
        return [ ('hdfs:filteredRules','?') ]
    
    def isTrue(self, flag, params):
        return params[flag][0].lower() == 't'
    
    def getCommands(self, params, inputs, outputs):
        
        mapper=('"./MapSubsampleRules --source_file `basename %(fFilterSet)s`'%inputs + 
            ' --buffer_size %(bufferSize)s"'%params)
        
        flags = ''
        for flag in ['NullRules', 'UseNULL', 'UseRefinedIBM1ProbEstimate', 'noAllowAbstractRules', 'noAllowRulesWithOnlyTargetTerminals']:
            if self.isTrue(flag, params): 
                flags += ' --%s'%flag
                
        reducer=('"./filterrules_bin %s '%flags +
                ' --lexical_weight_cutoff=%(lexicalWeightCutoff)s --PhrasalFeatureCount=%(phraseFeatureCount)s'%params + 
                ' --MeanTargetSourceRatio=`cat %(meanTargetSourceRatio)s`'%inputs +
                ' --cachesize %(cacheSize)s'%params +
                # TODO
                ' --LexicalWeightFile `basename %(lexPtgs)s`'%inputs+
                ' --LexicalWeightFileReversed `basename %(lexPsgt)s`'%inputs+
                ' --BeamFactorLexicalRules %(beamFactorLexicalRules)s'%params +
                ' --BeamFactorNonLexicalRules %(beamFactorNonLexicalRules)s'%params +
                ' --MinOccurrenceCountLexicalrules %(minOccurrenceCountLexicalRules)s'%params +
                ' --MinOccurrenceCountNonlexicalrules %(minOccurrenceCountNonlexicalRules)s'%params +
                ' --r `pwd`/%(fFilterSet)s'%inputs+
                ' --MaxSourceLength %(maxSourceLength)s'%params +
                ' --mapreduce_input --output_hdfs"')

        return ['hadoop jar $HADOOP_HOME/hadoop-streaming.jar -Dmapred.map.tasks=%(numMapTasks)s -Dmapred.reduce.tasks=%(numReduceTasks)s -Dmapred.job.queue.name=%(queueName)s '%params +
            ' -Dmapred.job.reduce.memory.mb=2048 -Dmapred.job.map.memory.mb=2048 -Dmapred.text.key.partitioner.options=-kn' +
            ' -Dstream.non.zero.exit.is.failure=true -Dmapred.job.name="SAMT Filter Rules and Add Instance Features"' +
            ' -input %(hdfs:unfilteredRules)s -file %(fFilterSet)s'%inputs +
            ' -output %(hdfs:filteredRules)s'%outputs +
            ' -mapper %s'%mapper +
            ' -reducer %s'%reducer +
            ' -file %(lexPsgt)s %(lexPtgs)s'%inputs +
            ' -file ./O2/MapSubsampleRules -file ./scripts/filterrules_bin' ]
    
    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = SamtFilterRules()
    t.handle(sys.argv)
