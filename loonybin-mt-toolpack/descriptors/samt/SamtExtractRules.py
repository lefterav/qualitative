from loonybin import Tool
from HadoopTool import HadoopTool

class SamtExtractRules(Tool):
    
    def __init__(self):
        self.hadoop = HadoopTool()
    
    def getName(self):
        return 'Machine Translation/SAMT/Extract Rules and Add MLE Feature'
    
    def getDescription(self):
        return """
        Extract Rules using either Hiero or SAMT-style heuristics and adds P(T|S) Feature
        """
    
    def getRequiredPaths(self):
        return ['samt']

    def getParamNames(self):
        params = self.hadoop.getSharedParams(False)
        # Extract params
        params.extend([
                        ('stopWordList','underscore-delimited list of tokens that WHAT DO THEY DO (default: ,_.)'),
                        ('maxSourceSymbolCount','maximum count of source-side symbols for extracted rules (default: 5)'),
                        ('allowDoublePlus','?'),
                        ('unaryCategoryHandling','WHAT ARE THE POSSIBILITIES'),
                        ('labeledGlueRules','WHAT ARE THE POSSIBILITIES'),
                        ('naturalSentenceRules','WHAT ARE THE POSSIBILITIES'),
                        ('allowAbstractSrc','?'),
                        ('allowConsecutiveNonterms','?'),
                        ('useOnlyPos','?'),
                        ('restrictToSet','Should we only extract rules for a particular dev and test set?')
                        ])
        # Merge params
        params.extend([
                        ('lexMinFreq','? (default: 2)'),
                        ('nonLexMinFreq','? (default: 4)'),
                        ('minFreqGivenSrcArg','? (default: 0.04)'),
                        ])
        return params
    
    def getInputNames(self, params):
        restrictToSet = Tool.isTrue(self, params['restrictToSet'])
        inputs = [ ('hdfs:phraseInstances','?') ]
        if restrictToSet:
            inputs.append( ('sourceRestrictFile','combined dev and test sets; only rules from these test sets will be extracted') )
        return inputs

    def getOutputNames(self, params):
        return [ ('hdfs:ruleInstances','?') ]
    
    def getCommands(self, params, inputs, outputs):
        restrictToSet = Tool.isTrue(self, params['restrictToSet'])
        mapper=('"runexp.sh perl -C extractrulesfeeder.pl | ./MapExtractRules' +
            ' --stop_word_list %(stopWordList)s --max_source_symbol_count %(maxSourceSymbolCount)s --allow_double_plus %(allowDoublePlus)s '%params +
            ' --unary_category_handling %(unaryCategoryHandling)s --labeled_glue_rules %(labeledGlueRules)s'%params +
            ' --natural_sentence_rules %(naturalSentenceRules)s'%params +
            ' --allow_src_abstract %(allowAbstractSrc)s --allow_consec_src_nts %(allowConsecutiveNonterms)s'%params +
            ' --use_only_pos %(useOnlyPos)s --mapreduce_output true"'%params)
        if restrictToSet:
            mapper += ' --source_restrict_file %(sourceRestrictFile)s'%inputs
        
        reducer=('"./MergeRules --lexminfreq %(lexMinFreq)s --nonlexminfreq %(nonLexMinFreq)s'%params +
            ' --min_freq_given_src_arg %(minFreqGivenSrcArg)s --mapreduce_input true"'%params)
            
        return ['hadoop jar $HADOOP_HOME/hadoop-streaming.jar -Dmapred.map.tasks=%(numMapTasks)s -Dmapred.reduce.tasks=%(numReduceTasks)s -Dmapred.job.queue.name=%(queueName)s '%params +
                    ' -Dmapred.job.reduce.memory.mb=2048 -Dmapred.job.map.memory.mb=2048' +
                    ' -Dstream.non.zero.exit.is.failure=true -Dmapred.job.name="SAMT Extract Rules and Add P(T|S) Features"' +
                    ' -input %(hdfs:phraseInstances)s '%inputs +
                    ' -output %(hdfs:ruleInstances)s'%outputs +
                    ' -mapper %s'%mapper +
                    ' -reducer %s'%reducer +
                    ' -file ./scripts/extractrulesfeeder.pl -file ./scripts/runexp.sh -file ./O2/MapExtractRules -file ./O2/MergeRules' ]
            
    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = SamtExtractRules()
    t.handle(sys.argv)
