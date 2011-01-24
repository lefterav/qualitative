from loonybin import Tool
from libmoses import *

class Moses(Tool):
    
    def getName(self):
        return 'Machine Translation/Decoders/Moses'
    
    def getDescription(self):
        return """
Takes a translation grammar, glue grammar, language model, and lexicalized 
distortion model and produces n-best translation hypotheses using Jon's working
copy of Joshua.
"""
    
    def getRequiredPaths(self):
        return ['moses']

    # Decoder params shared with MERT
    def getSharedParams(self):
         return [ ('numLMs', 'number of language models to use', '1'),
				  ('lmOrder', 'n-gram order of all language models', '5'),
				  ('lmLibrary', 'either srilm or irstlm', 'srilm'),
                  ('roModelType', 'type of reordering model', 'distance'),
                  ('ttableLimit', 'maximum number of target sides to be loaded for each source side', '40'),
                  ('distortionLimit', 'maximum phrase-wise window size within which phrases can reorder', '0'),
                  ('nBestSize', 'number of entries to output in n-best list', '1'), ]

    def getParamNames(self):
        params = self.getSharedParams()
        return params
       
    def getNumLms(self, params):
		try:
		 	return int(params['numLMs'])
		except:
			return  0
   
    # Decoder params shared with MERT
    def getSharedInputs(self, params):
		list = [ ('ptFile', 'Moses format phrase table') ]
		numLms = self.getNumLms(params)
		for i in xrange(numLms):
			if i == 0:
				list.append(('lmFile', 'ARPA format language model'))
			else:
				list.append(('lmFile%d'%(i+1), 'ARPA format language model #%d'%(i+1)))
        
		distRO = (params['roModelType'] == 'distance')
		if not distRO:
			list.append(('roFile', 'Moses format lexicalized reordering table'))
		return list

    def getInputNames(self, params):
        inputs = self.getSharedInputs(params)
        inputs.extend([ ('fSentsIn', '"French" sentences for which n-best hypotheses will be produced'),
                        ('optimizedConfigFile', 'Final configuration file resulting from MERT containing optimized feature weights') ])
        return inputs

    def getOutputNames(self, params):
        return [ ('eNBestOut', '"English" n-best hypotheses in Moses format (includes raw feature data)') ]
    
    def makeConfigFileCommands(self, params, inputs, configFileName):
           
        # TODO: Read LM order from arpa file?
        
        lmLib = params['lmLibrary'].lower()
        if lmLib == 'srilm':
        	lmLibNumber = '0'
        elif lmLib == 'irstlm':
        	lmLibNumber = '1'
        else:
        	raise Exception('Unrecognized LM library name: ' + lmLib)
        
        commands = []
        commands.append(r"nPtFeatures=$(head -n 1 %(ptFile)s | awk -F' \\|\\|\\| ' '{print $3}' | awk '{print NF}')" % inputs)

        # set bash $memoryTable to '0 ' or '' depending on version of Moses
        commands.append("if [[ $(egrep -c '(\$[a-z]+, \$b, \$c, \$d, \$fn)' ./scripts/training/absolutize_moses_model.pl) == '1' ]]; then memoryTable='0 '; else memoryTable=''; fi")
        
        mosesConfig = []
        mosesConfig.append('[input-factors]')
        mosesConfig.append('0')
        mosesConfig.append('')
        mosesConfig.append('[mapping]')
        mosesConfig.append('0 T 0')
        mosesConfig.append('')
        mosesConfig.append('[ttable-file]')
        mosesConfig.append('${memoryTable}0 0 $nPtFeatures %(ptFile)s' % inputs)
        mosesConfig.append('')
        mosesConfig.append('[lmodel-file]')
        numLms = self.getNumLms(params)
        for i in xrange(numLms):
			if i == 0:
				lmFile = inputs['lmFile']
			else:
				lmFile = inputs['lmFile%d'%(i+1)]
			mosesConfig.append(lmLibNumber + ' 0 %(lmOrder)s' % params + ' ' + lmFile)
        
        distRO = (params['roModelType'] == 'distance')
        if not distRO:
        	commands.append(r"nRoFeatures=$(head -n 1 %(roFile)s | awk -F' \\|\\|\\| ' '{print $NF}' | awk '{print NF}')" % inputs)
	        mosesConfig.append('')
	        mosesConfig.append('[distortion-file]')
	        mosesConfig.append('0-0 %(roModelType)s $nRoFeatures' % params + ' %(roFile)s' % inputs)
	        
        mosesConfig.append('')
        mosesConfig.append('[ttable-limit]')
        mosesConfig.append('%(ttableLimit)s' % params)
        mosesConfig.append('0') # load all elements
        mosesConfig.append('')
        mosesConfig.append('[distortion-limit]')
        mosesConfig.append('%(distortionLimit)s' % params)
        mosesConfig.append('')
        
        for line in mosesConfig:
            commands.append('echo "' + line + '" >> ' + configFileName)
            
        # get model weights from paramFile (if paramFile defined -- not true for tuning)
        if 'optimizedConfigFile' in inputs:
            # Extract only lines pertaining to weights from the optimized config file
            commands.append(r"awk '{if(/\[weight/) {inWeight=1} if(inWeight) {print} if(/^$/) {inWeight=0} }' %(optimizedConfigFile)s" % inputs + 
                                ' >> ' + configFileName)
        
            
        return commands
    
    def getCommands(self, params, inputs, outputs):
     
        commands = self.makeConfigFileCommands(params, inputs, 'moses.ini')
        cmd1 = ('./moses-cmd/src/moses -f moses.ini -i %(fSentsIn)s ' % inputs + 
                '-n-best-list %(eNBestOut)s ' % outputs + 
                '%(nBestSize)s distinct ' % params )
        commands.append(cmd1)
        return commands

    def getStatus(self, params, inputs):
        return [ 'done=$(wc -l < moses.out.stdout)',
                 'todo=$(wc -l < inputs/fSentsIn)',
                 'percent=$(echo "scale=2; $done*100/$todo" | bc)',
                 'echo "$done/$todo ($percent%)"' ]

    def getPostAnalyzers(self, params, inputs, outputs):
        # TODO: More detailed analysis of output
        #cmd = ('extract_feature_data.py %(eNBestOut)s'%outputs +
        #       ' %(optimizedConfigFile)s'%inputs)
        return [ ]

if __name__ == '__main__':
    import sys
    t = Moses()
    t.handle(sys.argv)
