from loonybin import Tool

class Joshua(Tool):
    
    def getName(self):
        return 'Machine Translation/Decoders/Joshua'
    
    def getDescription(self):
        return 
        
        """
        Takes a translation grammar, glue language model, and lexicalized 
        distortion model and produces n-best translation hypotheses using Jon's working
        copy of Joshua.
        """
    
    def getRequiredPaths(self):
        return ['joshua', 'joshua-jar', 'srilm-lib', 'mt-analyzers']

    # Decoder params shared with MERT
    def getSharedParams(self):
         return [ ('lmOrder', 'Maximum n-gram length to be read from the language model'),
                 ('spanLimit', 'Longest source-side token span to which a rule from the primary grammar can apply'),
                 ('defaultNonterm', 'Non-terminal symbol assigned to OOV words'),
                 ('maxItemsPerBin', 'Beam size per sentence span i,j (default: 30)'),
                 ('itemRelativeThreshold', 'Relative threshold for pruning items; how much worse can a new item be than the current BEST item and still be retained in the beam? (default: 10.0)'),
                 ('uniqueNBest','Should entries in the n-best list be checked for yield uniqueness within each sentence? (default: true)'),
                 ('treeNBest','Should entries in the n-best list show their derivation trees? (default: false)'),
                 ('includeAlign','Include source-span alignments for each non-terminal in the target tree? (default: false)'),
                 ('useDefaultGlue','Use the default glue grammar, which is appropriate for Hiero-style grammars with one X non-terminal'),
                 ('markOovs','Append _OOV to tokens that are out of vocabulary for the translation model?'),
                 ('nBest','How many entries should be produced for each sentence? (NOTE: Should be larger for tuning)'),
                 ('numThreads', 'Number of concurrent threads to be used for decoding') ]

    def getParamNames(self):
        params = self.getSharedParams()
        params.extend([ 
                ('heapSizeInMegs', 'Amount of memory allocated to the Java Virtual Machine\'s heap during decoding')
                ])

        return params
   
    # Decoder params shared with MERT
    def getSharedInputs(self, params):
        inputs = [ ('lmFile', 'ARPA format language model'),
                 ('tmFile', 'Combined phrase table and grammar in Joshua format') ]
        if not self.isTrue(params['useDefaultGlue']):
        	inputs.append( ('glueFile', 'Glue rules in Joshua format') )
        return inputs

    def getInputNames(self, params):
        inputs = self.getSharedInputs(params)
        inputs.extend([ ('fSentsIn', '"French" sentences for which n-best hypotheses will be produced'),
                        ('weightsFile', 'Optimized weights for the decoder\'s models') ])
        return inputs

    def getOutputNames(self, params):
        return [ ('eNBestOut', '"English" n-best hypotheses in Joshua format for the fSentsIn') ]
    
    def makeConfigFileCommands(self, params, inputs, configFileName):
           
        # TODO: Read LM order from arpa file?
        commands = []
        joshuaConfig = []
        joshuaConfig.append('lm_file=%(lmFile)s'%inputs)
        joshuaConfig.append('tm_format=hiero')
        joshuaConfig.append('tm_file=%(tmFile)s'%inputs)
        joshuaConfig.append('goal_symbol=S')
        joshuaConfig.append('glue_format=hiero')
        if not self.isTrue(params['useDefaultGlue']):
                joshuaConfig.append('glue_file=%(glueFile)s'%inputs)
        else :
                #create file now
                commands.append('echo "[S] ||| [X,1] ||| [X,1] ||| 0 0 0" >> hiero.glue')
                commands.append('echo "[S] ||| [S,1] [X,2] ||| [S,1] [X,2] ||| 0.434294482 0 0" >> hiero.glue')
                joshuaConfig.append('glue_file=hiero.glue')

        
        # lm config
        joshuaConfig.append('use_srilm=true') # always use srilm
        joshuaConfig.append('lm_ceiling_cost=100') # fix ceiling at 100
        joshuaConfig.append('use_left_equivalent_state=false') # paper said this takes longer; disable
        joshuaConfig.append('use_right_equivalent_state=false')
        joshuaConfig.append('order=%(lmOrder)s'%params)

        #tm config
        joshuaConfig.append('#TM config')
        joshuaConfig.append('span_limit=%(spanLimit)s'%params)
        joshuaConfig.append('phrase_owner=pt') # fixed
        joshuaConfig.append('mono_owner=mono') # fixed
        joshuaConfig.append('begin_mono_owner=begin_mono') # fixed
        joshuaConfig.append('default_non_terminal=%(defaultNonterm)s'%params)
        joshuaConfig.append('goalSymbol=S')
        joshuaConfig.append('mark_oovs=%(markOovs)s'%params)

        #pruning config
        joshuaConfig.append('fuzz1=0.1') # Fuzz (precision) for prepruning deductions in cube pruning
        joshuaConfig.append('fuzz2=0.1') 
        #fuzz2=0.1 $ Fuzz (precision) for pruning unlikely productions in cube pruning?
        joshuaConfig.append('max_n_items=%(maxItemsPerBin)s'%params)
        joshuaConfig.append('relative_threshold=%(itemRelativeThreshold)s'%params)
        joshuaConfig.append('max_n_rules=50') # Currently unused 
        joshuaConfig.append('rule_relative_threshold=10.0') # Currently unused

        #nbest config
        joshuaConfig.append('use_unique_nbest=%(uniqueNBest)s'%params)
        joshuaConfig.append('use_tree_nbest=%(treeNBest)s'%params)
        joshuaConfig.append('include_align_index=%(includeAlign)s'%params)
        joshuaConfig.append('add_combined_cost=true') # fixed; why not?
        joshuaConfig.append('top_n=%(nBest)s'%params)

        #remoter lm server config,we should first prepare remote_symbol_tbl before starting any jobs
        joshuaConfig.append('use_remote_lm_server=false')
        #remote_symbol_tbl=./voc.remote.sym
        #num_remote_lm_servers=4
        #f_remote_server_list=./remote.lm.server.list
        #remote_lm_server_port=9000

        #parallel deocoder: it cannot be used together with remote lm
        joshuaConfig.append('num_parallel_decoders=%(numThreads)s'%params)
        joshuaConfig.append('parallel_files_prefix=.') # fixed

        #disk hg
        joshuaConfig.append('save_disk_hg=false') # don't save hypergraphs for now
        
        
        for line in joshuaConfig:
            commands.append("echo '" + line +  "' >> " + configFileName)
        
        
        # get model weights from paramFile (if paramFile defined -- not true for tuning)
        if 'weightsFile' in inputs:
            commands.append("sed 's/||| //g' %(weightsFile)s >> "%inputs + configFileName)
            
        return commands
    
    def getCommands(self, params, inputs, outputs):
     
        commands = self.makeConfigFileCommands(params, inputs, 'joshua.config')
        
        ldPath = ('export LD_LIBRARY_PATH=.')
        commands.append(ldPath)
     
        cmd1 = ('java  -classpath joshua.jar -Djava.library.path=./lib -Xmx%(heapSizeInMegs)sM '%params + 
                'joshua.decoder.JoshuaDecoder joshua.config %(fSentsIn)s '%inputs +
                '%(eNBestOut)s'%outputs)
        commands.append(cmd1)
        return commands
    
    def getPreAnalyzers(self, params, inputs):
        cmd1 = ('./analyze-srilm.py %(lmFile)s'%inputs)
        #cmd2 = ('./find_oovs.py %(tmFile)s %(lmFile)s %(fSentsIn)s'%inputs)
        return [ cmd1 ]

    def getPostAnalyzers(self, params, inputs, outputs):
        # TODO: Make sure we have the same number of output hypotheses as inputs
        #cmd = ('AnalyzeParCorpus.sh %(fCorpusOut)s %(eCorpusOut)s'%outputs
        #       )
        cmd = ('extract_feature_data.py %(eNBestOut)s'%outputs +
               ' %(weightsFile)s'%inputs)
        return [ cmd ]

if __name__ == '__main__':
    import sys
    t = Joshua()
    t.handle(sys.argv)
