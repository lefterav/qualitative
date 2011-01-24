
RO_MODEL_TYPES = ('msd-bidirectional-fe (default), msd-bidirectional-e, msd-fe, msd-f, ' +
				'monotonicity-bidirectional-fe, monotonicity-bidirectional-f, monotonicity-fe, monotonicity-f')

def getDummyMosesCommands():
    return [ 'mkdir dummyBin',
                'touch dummyBin/mkcls dummyBin/GIZA++ dummyBin/snt2cooc.out',
                'chmod +x dummyBin/*',
                'mkdir model' ]

# sets bash $script to path of train-model.perl script
def getMosesScriptFinder():
    return [ 'if [ -e ./scripts/training/train-factored-phrase-model.perl ]; then script=./scripts/training/train-factored-phrase-model.perl; else script=./scripts/training/train-model.perl; fi' ]

