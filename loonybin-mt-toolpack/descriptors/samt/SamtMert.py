from loonybin import Tool
from HadoopTool import HadoopTool
from SamtDecode import SamtDecode

class SamtMert(Tool):
    
    def __init__(self):
        self.hadoop = HadoopTool()
        self.decoder = SamtDecode()
    
    def getName(self):
        return 'Machine Translation/SAMT/SAMT MERT'
    
    def getDescription(self):
        return """
        Run Minimum Error Rate Training to tune the weights of a SAMT System.
        """
    
    def getRequiredPaths(self):
        return ['samt']
    
    def getMParams(self):
        return [ ('ScoringMetric','?'),
                 ('Opti_Epsilon','?') ]

    def getParamNames(self):
        params = self.hadoop.getSharedParams(False)
        params.extend(self.decoder.getTParams())
        params.extend([ ('nRefs','?'),
                       ('initialParams','? example: ???'),
                       ('iter_limit','maximum number of MERT iterations'),
                       ('merge_tasks','?'),
                       ('mer_random_restarts','?'),
                       ('mer_zero_out_dims','?'),
                       ('mer_runs_per_iteration','?'), ])
        params.extend(self.getMParams())
        return params
    
    def getInputNames(self, params):
        inputs = self.decoder.getSharedInputs()
        inputs.extend([
                 ('fDevSents','?'),
                 ('eRefSents','?') ])
        return inputs

    def getOutputNames(self, params):
        return [ ('tunedParams','?'),
                 ('eSentsOut','?') ]
        
        
    def makeMertConfigFile(self, params, configFilename, paramsCommand, dfsDir):
        config = []
        config.append('no_hod=1') # Don't use Hadoop-on-demand
        config.append('target_word_factors=1')
        config.append('dfs_dir=%s'%dfsDir)
        config.append('working_local_dir=.') # LoonyBin keeps things separated for us
        
        if 'nRefs' in params:
            config.append('dev_num_references=%s'%params['nRefs'])
        else:
            config.append('dev_num_references=1')
        
        config.append('iter_limit=%(iter_limit)s'%params)
        config.append('merge_tasks=%(merge_tasks)s'%params)
        config.append('mer_random_restarts=%(mer_random_restarts)s'%params)
        config.append('mer_zero_out_dims=%(mer_zero_out_dims)s'%params)
        config.append('mer_runs_per_iteration=%(mer_runs_per_iteration)s'%params)
        
        #config.append('wts=`%s`'%paramsCommand)
        
        # MER params
        merParams = ' '.join([ '--%s %s'%(name, params[name]) for name, desc in self.getMParams() ])
        config.append('mer_params="%s"'%merParams)
        
        commands = ["echo '%s' >> %s"%(line, configFilename) for line in config]
        return commands
    
    def getCommands(self, params, inputs, outputs):
        paramsCommand = 'echo %(initialParams)s'%params
        dfsDir = '%(hdfs:)s'%outputs
        srcAndRefsDir = dfsDir + '/experimentName/src_and_refs_dev'
        
        commands = []
        commands.append('# Create expt directory to fool SAMT into thinking we execute from the O2 directory')
        commands.append('mkdir expt && cd expt')
        commands.append('# Symlink in executable files that are not symlinks')
        commands.append("find ../O2/ -maxdepth 1 \\"+
                            "-perm -a+x \\"+
                            "! -type l \\"+
                            "! -type d  \\"+
                            "-exec sh -c 'exec ln -sf \"$@\" .' inline-cmd {} +")
        commands.extend(self.decoder.makeConfigFile(params, inputs, 'translate.params', paramsCommand, dfsDir))
        commands.extend(self.makeMertConfigFile(params, 'mer.params', paramsCommand, dfsDir))
        commands.append('hadoop dfs -cp %(hdfs:filteredRules)s'%inputs + ' %(hdfs:)s/experimentName/filter_rules_dev'%outputs)
        commands.append('hadoop dfs -cp %(hdfs:filteredLM)s'%inputs + ' %(hdfs:)s/experimentName/filter_lm_dev'%outputs)
        commands.append('hadoop dfs -mkdir '+srcAndRefsDir)
        commands.append('cat ../%(fDevSents)s | sbmtpreprocess.pl'%inputs+
             ' | perl ../m45scripts/create_mr_corpora.pl --num_parts 0 --source_file -'+
             ' --reference_file ../%(eRefSents)s'%inputs+
             ' --num_references %(nRefs)s'%params+
             ' --output_dir ' + srcAndRefsDir+
             ' --output_prefix src-part')
        commands.append('mer_loop.sh experimentName translate.params mer.params')
        commands.append('cd ..')
        return commands
    
    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = SamtMert()
    t.handle(sys.argv)
