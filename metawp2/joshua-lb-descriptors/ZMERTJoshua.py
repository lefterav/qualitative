from loonybin import Tool
from Joshua import Joshua

class ZMERT(Tool):
    
    def __init__(self):
        self.decoder = Joshua()
    
    def getName(self):
        return 'Machine Translation/Tuning/Z-MERT -- Joshua'
    
    def getDescription(self):
        return "Tunes a translation system, decoding with Jon's working copy of Joshua and optimizing using Z-MERT."
    
    def getRequiredPaths(self):
        return ['joshua', 'srilm-lib', 'mt-analyzers' ]

    def getParamNames(self):
        params = self.decoder.getSharedParams()
        params.extend([ ('heapSizeInMegs', 'Amount of memory allocated to the Java Virtual Machine\'s heap during decoding'),
                 ('metric', 'Metric to be optimized toward and its parameters'),
                 ('maxIts', 'Maximum number of decoding-optimization iterations to be performed'),
                 ('randomRestarts', 'Number of times to restart from a random point in the search space (?)'),
                 ('nbestSize', 'Desired size of the n-best list (MUST MATCH DECODER CONFIG FILE)'),
                 ('stopSig', 'Value over which a weight change is "significant" (for early exit purposes)') ])
        return params

    def getInputNames(self, params):
        inputs = self.decoder.getSharedInputs(params)
        inputs.extend([('fDevSents', '"French" sentences from tuning set'),
                 ('eRefSents', '"English" reference sentences from tuning set. Format: all references corresponding to the same sentence, newline-delimited , then a trailing newline'),
                 ('paramConfigFile', 'Initial MERT weights') ])
        return inputs

    def getOutputNames(self, params):
        return [ ('finalParams', 'A text format with the tuned parameters for each of the features in the given decoder configuration'),
				 ('eNBestOut','N-best list from the final iteration of MERT (NOTE: This is close, but not necessarily the same as decoding the dev set with the final tuned parameters)') ]
    
    def getCommands(self, params, inputs, outputs):
        
        # TODO: Process references into correct format using a ReferenceToJoshua.py script
        # TODO: Enforce size of N-best?
        
        #-cmd   ./decoder_command_ex2   # file containing commands to run decoder if running external
        # Create joshua.config on the fly
        commands = self.decoder.makeConfigFileCommands(params, inputs, 'joshua.config')
    

        #ZMERT CONFIGURATION
        commands.append('numRefs=$(( $( wc -l < %(eRefSents)s ) / $( wc -l < %(fDevSents)s ) ))'%inputs)
        zmertConfig = dict()
        zmertConfig['dir'] = '.'
        zmertConfig['seed'] = '12341234'    # Random number generator seed
        zmertConfig['v'] = '1'    # verbosity level (0-2; higher value => more verbose)
        zmertConfig['decOut'] = 'nbest.out'    # file prodcued by decoder
        zmertConfig['rand'] = '0'    # should first initial point (of first iteration) be initialized randomly?
        zmertConfig['decV'] = '1'    # should decoder output be printed?
        zmertConfig['s'] = inputs['fDevSents']
        zmertConfig['r'] = inputs['eRefSents']
        zmertConfig['rps'] = '$numRefs'
        zmertConfig['p'] = "params.txt"
        zmertConfig['m'] = params['metric']
        zmertConfig['maxIt'] = params['maxIts']
        zmertConfig['ipi'] = params['randomRestarts']
        zmertConfig['dcfg'] = 'joshua.config'
        zmertConfig['N'] = params['nbestSize']
        zmertConfig['fin'] = outputs['finalParams']
        zmertConfig['stopSig'] = params['stopSig']

        # Create zmert.config on the fly
        for key, value in zmertConfig.iteritems():
            commands.append("echo \"-%s %s\" >> zmert.config"%(key, value))
        #commands.append("cp %(paramConfigFile)s params.txt"%inputs)
        # get feature names from paramConfigFile and give them all zero weight since MERT will set these 
        commands.append("sed 's/|||.*/ 0.0/g;s/normalization.*//g' %(paramConfigFile)s >> joshua.config"%inputs)
        commands.append("cp %(paramConfigFile)s params.txt"%inputs)  
        
        #DECODER COMMAND
        commands.append("echo \"java -Xmx1g -cp ./bin/joshua.jar -Djava.library.path=./lib -Dfile.encoding=utf8 joshua.decoder.JoshuaDecoder joshua.config %(fDevSents)s devset.output.nbest\" > decoder_command"%inputs)
        ldPath = ('export LD_LIBRARY_PATH=.')
        commands.append(ldPath)
        
        commands.append('java -cp bin/joshua.jar -Xmx%(heapSizeInMegs)sM -Djava.library.path=./lib joshua.zmert.ZMERT zmert.config | tee zmert.stdout'%params)
        
        # Get final n-best list
        commands.append('dir=`pwd`')
        commands.append('file=`ls -1t nbest.out.ZMERT.it* | head -1`')
        commands.append('ln -s $dir/$file %(eNBestOut)s'%outputs)

        return commands
    
    def getPreAnalyzers(self, params, inputs):
        cmd1 = ('./analyze-srilm.py %(lmFile)s'%inputs)
        cmd2 = ('java -cp ParCorpusAnalyzer.jar analyzers.PhraseTableAnalyzer %(tmFile)s'%inputs)
        #cmd3 = ('find_oovs.py %(tmFile)s %(lmFile)s %(fDevSents)s %(eRefSents)s'%inputs)
        return [ cmd1, cmd2 ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

    def getStatus(self, params, inputs):
        return [ "egrep -o 'iteration #[0-9]+' zmert.stdout | tail -1",
                 "fgrep 'Best final' zmert.stdout | egrep -o 'j=[0-9]+.*BLEU: [0-9.]+' | sed 's/]../ /g'"]

if __name__ == '__main__':
    import sys
    t = ZMERT()
    t.handle(sys.argv)
