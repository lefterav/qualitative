from loonybin import Tool
from HadoopTool import HadoopTool

class SamtDecode(Tool):
    
    def __init__(self):
        self.hadoop = HadoopTool()
    
    def getName(self):
        return 'Machine Translation/SAMT/SAMT Decoder'
    
    def getDescription(self):
        return """
        Decodes sentences from a held-out or unseen test set using the SAMT decoder.
        """
    
    def getRequiredPaths(self):
        return ['samt']
    
    def getTParams(self):
        return [
                ('AllowConsecSrcNonterminals', 'false means make decoder run faster if you dont allow 2 non-terminal consecutive during decoding'),
                ('MaxAbstractionCount', 'tell decoder how many non-terminal allow per rule; synchronize with rule extraction can check for rule extraction by running MapExtractRules ; FastTranslateChart for defalt param decoder'),
                ('SRIHistoryLength', '4 means use 5-gram LM'),
                ('HistoryLength', '2 means only look back 2 token during the chart parsing; value must be <= SRIHistoryLength if HistoryLength < SRIHistoryLength then RecomputeLMCostsDuringNBest has to be 1'),
                ('RecomputeLMCostsDuringNBest', 'rescoring Nbest during nbest list extraction from hypergraph'),
                ('RescoreLM', 'when already have nbest list'),
                ('ComboPruningBeamSize', 'prunning with LM , cube-prunning'),
                ('PruningMap', '??? - 0-25-inf-@_S-50-inf'),
                ('MaxHypsPerCell', '300 means keep 300 hyps per cell (equivalent ~ 12 buckkets = 300/25)'),
                ('MaxCombinationCount', '15 means after 15 words, only do GLUE rules'),
                ('MaxCombinationCount80words', '10 means if having a sentence with 80 words then start GLUE rule at 10'),
                ('RemoveUnt', '0 means do not remove untranslated words'),
                ('TagSetList', 'if want to use some tags as @number_tag'),
                ('ScoringMetric', 'IBMBLEU/NISTBLEU/NIST'),
                ('DisplayNBestData','always same as NBest'),
                ('ExtractUnique', '1 means creating unique NBEST'),
                ('v', 'verbosity if set to high number then see a lot of infomation')
                ]
#tparams="--NormalizingScript ./simple_normalize_bin --AllowConsecSrcNonterminals false --MaxAbstractionCount 
#2 --RecomputeLMCostsDuringNBest 1 --RescoreLM 0 --SRIHistoryLength 4 --HistoryLength 2 --PruningMap 0-25-inf-
#@_S-50-inf --ComboPruningBeamSize 100 --MaxCostDifferencePerCell inf --MaxHypsPerCell 300 --MaxCombinationCou
#nt 15 --MaxCombinationCount80words 8 --RemoveUnt 0 --MaxRuleAppCountDifference 10 --TagSetList @_dummy --Scor
#ingMetric IBMBLEU --DisplayNBestData 100 --NBest 100 --ExtractUnique 1 --v 0"
    
    # DEPRECATED
    def getAllSharedParams(self):
        return [
            ("addboseosinternally","(0): Assume input sentences of the form <s> ... </s>; (1) Add <s> and </s> internally to the input sentences)","1"),
            ("allowconsecsrcnonterminals","If your non-glue grammar rules don't have consecutive nonterminals on the source side (as in Chiang), setting this to false will speed up decoding as futile lookup attempts will be avoided. Rules involving underscored NTs @_S, @_G, @_R will always be allowed through.)","1"),
            ("astarbeam","Per word beam for A* search step)","inf"),
            ("beamsizefactor","during N-best retrieval the temporary size of the beam will be N*BeamSizeFactor - set this to a value higher than 1 if you are forcing unique extraction (ExtractUnique=1) or if you don't do LM intersection (CompareTargetWords=0))","10"),
            ("breadthastar","Do AStar by breadth )","1"),
            ("combopruningbeamsize","When combing the incomplete hyp and a rule for a particular cell we can do some lossy pruning here to avoid calculating LM scores for all the completed hyps most of which will be discarded. This is the max. n.o. hyps considered per coarse-grained EC (you can also use inf denoting infinity here))","10000"),
            ("combopruningfuzzcostdifference","Allowed cost (neg-log prob) a hyp during ComboPruning is allowed to differ from last officially allowed cost (i.e from bestHypCost+PruningMapCostDifference) to still be included into the combo pruning beam. However such an element is only put on the beam if ComboPruningBeamSize has not been exceeder yet. Further elements are added to the beam *disregarding* ComboPruningFuzzCostDifference as long as ComboPruningMinBeamSize has not been exceeded yet. You can also use inf denoting infinity here)","5"),
            ("combopruningglobal","Combo pruning can be done within a single matched <incomplete-hyp,rule> pair (0), or globally across all matched pairs in a chart cell that have identical LHS nonterminals (1), or globally across all matched pairs in a chart cell, regardless of LHS nonterminal (2))","1"),
            ("combopruningminbeamsize","When combing the incomplete hyp and a rule for a particular cell we can do some lossy pruning here to avoid calculating LM scores for all the completed hyps most of which will be discarded. This is the min. n.o. hyps considered per coarse-grained EC)","30"),
            ("combopruninguselm","Use the LM during ComboPruning should trigger the k-best seearch to add a few additional neighbors down in case they end up filter upto the top )","1"),
            ("comparetargetwords","Each cell in the parsing contains several equivalence classes - hyp classes that cannot be compared and pruned away because hyps from that class my give best performance when combined later. Setting CompareTargetWords==1 use LM context length as a separator if you use this you MUST use the PruningMap )","1"),
            ("displaynbestdata","Write out translation model scores and path for DisplayNBestData UNIQUE elements in the n-best list)","40"),
            ("dontreloadbeam","Dont reload the beam in astar )","0"),
            ("extractrecombine","In the A* style search form equivalence classes on the fly and drop hyps that are re-combined)","1"),
            ("extractunique","Force the nbest list extraction to extract NBest unique translations - must set BeamSizeFactor>1 will slow down retrieval   )","1"),
            ("featureweightsparsing","Feature weights (when doing MER training these are the initial values) separated by commas)"),
            ("featureweightsrescoring",")"),
            ("fullsentnonterminal","The nonterminal marker for a complete sentence signals also when EOS BOS can be used)","@_S"),
            ("futurecostimpact","Undocumented and not important. Always use 1.0 for CompareTargetWords==1 possibly use lower values for CompareTargetWords=0)","1"),
            ("gainfile","information Gain file for NIST scoring  )"),
            ("genoraclescores","saves nbest lists across iterations of MER (more memory) and outputs an Oracle score after each iteration)","1"),
            ("globallmcache","If non-zero we will never clear the LM cache. If zero we'll clear it after each sentence.)","0"),
            ("glueandeosassumptions","If set to nonzero will assume our kind of glue rules and our kind of rules involving </s>. This will cause optimizations to make parsing faster and also will cause assertions checking that the glue rule is firing. If you set this to zero you might want to also set MaxRuleAppCountDifference to a very high number.)","1"),
            ("historylength","History length assumed for the language models: this will determine the length of the first-words and last-words of a hyp's m_lmContext and thus the granularity of the equivalence classes. This value needn't necessarily correspond to the true Markov-order of the LMs.)","2"),
            ("hypspernode","This param exists only for compatibility and is ignored. Used to be: number of complete hypotheses a hypergraph node can maximally hold (exception: the _S node will keep all its hyps))","0"),
            ("iterationlimit","Limit to the number of iterations that MER will be run for)","1"),
            ("lmfiles","Filename(s) for the language models used. If more than one separate them by comma. If the file has the extension '.samtlm' we will assume it to be an SAMT language model; if the file extension is '.srilmbackward' we will assume it to be an SRI LM trained on reversed (last word first) sentences; if the extension is '.srilm' we assume it to be a regular SRI language model.)"),
            ("lmprefix","The prefix for each lm. LM names should be LMPrefix-ruleno)","lm"),
            ("mapreduce_input","If this parameter is set, input sentences are of the form <partnum      snum      src_words      ref1      refN>. The part number is used because the translator will be running in the reduce step and we want control of sharding)","0"),
            ("maxabstractioncount","The maximum number of abstractions per rule. If your grammar only uses two (as in Chiang), lowering this value to 2 will speed up decoding as futile lookup attempts will be avoided.)","1000000"),
            ("maxcombinationcount","Limit on span of non glue rules - effectively a time out for the expensive parsing step)","10"),
            ("maxcombinationcount80words","Limit on span of non glue rules for sentences of 80 or more words (if this number is larger than MaxCombinationCount then MaxCominationCount will be used instead) - effectively a time out for the expensive parsing step)","5"),
            ("maxcostdifferencepercell","Max. allowed cost that a hyp can deviate from the best hyp in its cell (inf: any cost allowed). LHS @_X, @_S, and @_G hyps always get through -- therefore this param is only relevant for non-Chiang mode. This enables pruning across coarse-grained ECs. Used in PruneCell)","inf"),
            ("maxfeatureweightsparsing","Maximum-values allowed for each feature weight separated by commas. By default we assign 100 to all)"),
            ("maxfeatureweightsrescoring",")"),
            ("maxhypspercell","Max. allowed n.o. hyps per chart cell, not counting LHS @_X, @_S, and @_G hyps (they always get through -- therefore this param is only relevant for non-Chiang mode). This enables pruning across coarse-grained ECs. Used in PruneCell)","1000000000"),
            ("maxruleappcountdifference","Largest deviation of the rule-app-count feature from the lowest-rule-app-count hyp that a hyp can have in order to still be filed in the chart. Crucial pruning parameter. It relies on our type of glue rules though so if you are using different types of glue rules or not using the rule-app-count feature then set this value to a very high number.)","2"),
            ("maxsentenceprocessingtime","Maximum time in seconds that processing one sentence takes. Relevant only for Worker-bee mode: The worker bee will assume that a process got killed if nothing happened on a sentence for more than MaxSentenceProcessingTime seconds.)","480"),
            ("meroptimize","runs iterations of Minimum Error rate training on the nbest lists generated in each iteration)","0"),
            ("minfeatureweightsparsing","Minimum-values allowed for each feature weight separated by commas. By default we assign -100 to all)"),
            ("minfeatureweightsrescoring",")"),
            ("nbest","number of translations to put in the N-best list for parameter optimization)","1000"),
            ("nbest_min","Base value of working NBest for short sentences)","100"),
            ("nbest_mult","Treat the NBest value as a the base of an nbest^srclength if NBestMult==1 : nbest*srclength if NBestMult=2)","0"),
            ("nbeststyle","Style of n-best list retrieval (1==A* style) (2==HC05))","2"),
            ("nbestsubspans","Use NBest extraction from the sub-spans 0 (dont do sub span addition) 1 (do it with just cell m_maxCombinationCount 1) 2( use the whole m_maxCombinationCount row)   )","0"),
            ("no_sample","If true and in MapReduce mode, only load a single rule file rule-0 for all sentences instead of rule-N for sentence N)","0"),
            ("norescoring","Don't optimize parsing features and rescoring features separately base everything on FeatureWeightsParsing and optimize only those if in MER-mode)","1"),
            ("normalizereferences","Normalize the references with the NormalizingScript (this is dangerous))","0"),
            ("normalizingscript","Normalizing script used on references and translation output - do things like lowercasing/truecasing/detokenization; each input line is a translation each output line is the normalized translation; script has to be executable and flush input and output buffer line-by-line; see example punctuation-postprocess-eval4.pl for required structure of perl script for Normalizing)"),
            ("numreferences","num references per source sentence )","1"),
            ("opti_donorm","Normalize scaling factors after each iteration )","1"),
            ("opti_epsilon","Optimize until the last dimension's error gain is within Opti_Epsilon of the previous value)","0"),
            ("opti_epsilonscale","Scale up the threshold when using two stage optimization to save time)","1"),
            ("opti_nummodify","Number of features that you try zeroing out per MER iteration (this starts with the first Opti_NumModify features and continues with the next Opti_NumModify in the next iteration step and so on modulo the n.o. features))","4"),
            ("opti_numpermutes","Number of times you change a few dimension and try to reconverg 1==just use what the initial values )","1"),
            ("opti_numstarts","Number of starts of f the optimizer 1==just use the initial values )","1"),
            ("opti_twostage","Run 2 stage optimization - nulling out certain fields and re-optimizing. Use this together with Opti_NumModify. Don't use this option AND Opti_NumStarts / Opti_NumPermutes > 1)","1"),
            ("pruningmap","Pruning options for each non-terminal (i.e. coarse-grained EC) specifying the max. n.o. hyps per result NT in each cell and the maximally allowed cost difference from the lowest-cost hyp across all fine-grained ECs of that result NT (all worse-cost hyps will be pruned away). (@X-10-2.5) means keep at most top 10 hyps in coarse-grained EC with LHS NT @X that are all at most 2.5 plus the cost of the top hyp. Use 0 instead of @X to define behavior for all NTs not otherwise specified. You can also specify the value inf (for infinity) as a cost-difference.)","0-100-5-@_S-200-5"),
            ("pruningmapuseboundary","Use the boundary words to pruning equivalence classes)","1"),
            ("ra_lowestcount","Use the lowest rule app count instead of the count of the lowest cost hyp)","0"),
            ("ra_mult","Use MaxRuleAppCountDifference as a multiplicative factor instead of a difference)","0"),
            ("ra_updatehyp","Update the hyp's rule app count with the fine-grained eq class counts)","1"),
            ("recomputelmcostsduringnbest","1: During N-best retrieval each time an underlying hypothesis is slurped in recompute all LM costs from scratch as we have more history context available now. This slows down K-best retrieval and is only useful when the Markov order of one of the LMs used is higher than --HistoryLength. You can also set this option to 2 which will recompute the LM cost and sanity-check that the results are the same as compared to only recomputing the LM costs necessary (use this as a sanity check if your LMs' Markov orders are all less or equal --HistoryLength).)","0"),
            ("referencelist","reference sentences for scoring )"),
            ("removeunt","Remove untranslated words from translation output (used during MER too))","0"),
            ("rescorelm","After the N best translations have been retrieved recompute their LM costs from scratch and re-sort the translations. The CPU time to do this is insignificant. You should only set this parameter to zero if the Markov order of your LMs is not higher than --HistoryLength. If --RecomputeLMCostsDuringKBest > 0 then --RescoreLM=1 won't have any effect. You can also set this option to 2 which will recompute the LM cost and sanity-check that the results are the same as they were after K-best retrieval (use this as a sanity check if your LMs' Markov orders are all less or equal --HistoryLength or you had --RecomputeLMCostsDuringKBest > 0).)","0"),
            ("rulesetdir","This parameter indicates where rule's sampled for each sentence can be found, in the format: RuleSetDir/RuleSetPrefix-0 where XXX is the sentence number matching this SentenceList. If RuleSetDir is prefixed with hdfs: then files will be copied down from hdfs)"),
            ("rulesetprefix","The prefix for each rule. Rule names should be RuleSetPrefix-ruleno)"),
            ("saveallalternatives","Keep all alternatives in the EqClass )","1"),
            ("scoringmetric","Scoring Metric to run MER or evaluate your translations against the reference)","IBMBLEU"),
            ("sentencelist","name of file that contains a list of sentences in plain text format)"),
            ("srihistorylength","Actual Markov order of the SRI language models used (e.g. 2 for trigram). Note that this is NOT used for determining the length of m_lmContext and thus the granularity of the equivalence classes (use parameter HistoryLength for that).)","2"),
            ("tagsetlist","Comma-separated list of tags: nonterminals that when occurring as LHS of an applied rule will be used directly (instead of the rule's translation output) when querying the LM model. Example: @CD @NUM @DATE)"),
            ("unknownword","All occurrences of the UnknownWord in the source side of rules in the rule database serve as templates for any word that is unknown (i.e. is not equal to any rule's source side).)","_UNKNOWN"),
            ("updatebeamsize","Try to ensure that we have BeamSizeFactor active hyps not just all hyps )","0"),
            ("userulepreferences","Whether to use an additional runtime feature that calculated how compatible composing rule nonterminals are)","0"),
            ("usespanfeatures","Whether to append feature vector by feature computing (up to a constant) the neg-log probability of the created complete hypothesis given only its source span length)","0"),
            ("v","Verbosity (0) for general experiments (1) to see the flow of the program (2) to debug problem areas)","0"),
            ("vocabulary","Optional. Name of file that contains the vocabulary will be augmented in memory based on vocab in rule database and test set. Becomes mandatory if an SAMT language model is used.)"),
            ("workerbeedir","If specified we use the worker-bee mode. Then this is the directory in which the Worker Bee files like locks and per-sentence n-best lists and MER params are stored.)"),
            ]

    def getSharedInputs(self):
        return [('normalizingScript', 'post-processing script (compile to binary by pp) in script dir'),
                ('hdfs:filteredLM','?'),
                ('hdfs:filteredRules','?')]

    def getParamNames(self):
        params = self.hadoop.getSharedParams(False)
        params.extend(self.getTParams())
        return params
    
    def getInputNames(self, params):
        inputs = self.getSharedInputs()
        inputs.extend([
                 ('fSentsIn','?'),
                 ('tunedWeights','?') ])
        return inputs        

    def getOutputNames(self, params):
        return [ ('eSentsOut','?'),
                 ('hdfs:dfsDir','a hack to appease the SAMT framework') ]
    
    def isTrue(self, flag, params):
        return bool(params[flag])
    
    def makeConfigFile(self, params, inputs, configFilename, paramsCommand, dfsDir):
        config = []
        config.append('no_hod=1') # Don't use Hadoop-on-demand
        config.append('target_word_factors=1')
        config.append('dfs_dir=%s'%dfsDir)
        #config.append('initial_local_dir=.') # No longer required
        config.append('working_local_dir=.') # LoonyBin keeps things separated for us
        
        if 'nRefs' in params:
            config.append('dev_num_references=%s'%params['nRefs'])
        else:
            config.append('dev_num_references=1')
        
        config.append('wts=`%s`'%paramsCommand)
        
        commands = ["echo '%s' >> %s"%(line, configFilename) for line in config]
        
        # Special handling for normalization script since it doesn't have absolute path
        tparams = ' '.join([ '--%s %s'%(name, params[name]) for name, desc in (self.getTParams()) ])
        commands.append('echo \'tparams="%s\''%tparams+
                        ' --NormalizingScript `pwd`/%s'%inputs['normalizingScript']+
                        '\'"\' >> %s'%configFilename)
        
        return commands
            
    
    def getCommands(self, params, inputs, outputs):
        paramsCommand = 'cat %(tunedWeights)s'%inputs
        dfsDir = '%(hdfs:dfsDir)s'%outputs # A Hack to make sure we have a directory to put things in
        commands = self.makeConfigFile(params, inputs, 'config.params', paramsCommand, dfsDir)
        
        srcAndRefsDir = '%(hdfs:)s/experimentName/src_and_refs_dev'%outputs
        commands.append('hadoop dfs -mkdir '+srcAndRefsDir)
#        commands.append("cat %(fSentsIn)s sbmtpreprocess.pl < $initial_local_dir/$src_file | perl ../m45scripts/create_mr_corpora.pl --num
#_parts $num_parts --source_file - --reference_file $initial_local_dir/$tgt_file --num_references $num_
#references --output_dir $dfs_dir/$src_and_refs --output_prefix src-part"
#sbmtpreprocess.pl < $initial_local_dir/$src_file | perl ../m45scripts/create_mr_corpora.pl --num_parts
# $num_parts --source_file - --reference_file $initial_local_dir/$tgt_file --num_references $num_refere
#nces --output_dir $dfs_dir/$src_and_refs --output_prefix src-part
        
        commands.append('ln -s dev.src %(fSentsIn)s'%inputs)
        commands.append('ln -s dev.tgt %(fSentsIn)s'%inputs) # Dummy file so evaluation doesn't crash
        commands.append('translate.sh experimentName config.params')
        return commands
    
    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = SamtDecode()
    t.handle(sys.argv)
