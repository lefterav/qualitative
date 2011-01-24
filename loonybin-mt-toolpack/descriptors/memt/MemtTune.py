from loonybin import Tool
from Memt import Memt

class MemtTune(Memt):
    
    def getName(self):
        return 'Machine Translation/MEMT/MEMT Tune'
    
    def getDescription(self):
        return "Tune weights for the MEMT system using Z-MERT"

    def getParamNames(self):
        return Memt.getSharedParams(self)

    def getInputNames(self, params):
        inputs = Memt.getSharedInputs(self)
        inputs.extend([
                       ('devMatchedFile','?'),
                       ('devRefFile','?')
                       ])
        return inputs

    def getOutputNames(self, params):
        return [ ('topbestOut', '?'),
                 ('nbestOut', '?'),
                 ('tunedWeights','?') ]
    
    def getCommands(self, params, inputs, outputs):
        commands = Memt.getStartServerCommands(self, params, inputs, outputs)
        commands.extend(Memt.makeConfigFile(self, params, 'decoder_config_base'))
        
        commands.append('ln -s %(devMatchedFile)s dev.matched'%inputs)
        commands.append('ln -s %(devRefFile)s dev.reference'%inputs)
        
        runClient = './scripts/zmert/run.rb $port .'%inputs
        commands.append(runClient)
        commands.extend(Memt.getKillServerCommands(self))
        
        commands.append('ln -s output.1best %(topbestOut)s'%outputs)
        commands.append('ln -s output.nbest %(nbestOut)s'%outputs)
        commands.append("awk -F'\"' '/score.weights/{print $2}' decoder_config > %(tunedWeights)s"%outputs)
        return commands
    
    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = MemtTune()
    t.handle(sys.argv)
