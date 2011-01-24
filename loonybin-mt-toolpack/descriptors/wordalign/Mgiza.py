from loonybin import Tool

# Common configuration for Qin's QMT Package including MGIZA and Chaksi
class Mgiza(Tool):
    
    # We use "f" to mean the "French" side with regard to *TRANSLATION DIRECTION*, odd noisy chanel terminology aside 
    
    def __init__(self, mode, isChaski):
        self.mode = mode
        self.isChaski = isChaski
        if self.mode == 'A':
            self.inputMode = '1'
            self.outputMode = '4'
        else:
        	self.inputMode = mode
        	self.outputMode = mode
        
        self.modelFiles = [
           # name, gizaParam, description, whenInput, whenOutput
           ('t1','previoust','p(f|e) Model 1 translation table','H','1'),
           ('thmm','previoust','p(f|e) HMM translation table','3','H'),
           ('t3','previoust','p(f|e) Model 3 translation table','4','34'),
           
           ('hhmm','previoushmm','x','34','H'),
           ('hmmAlpha','','x','34','H'),
           ('hmmBeta','','x','34','H'),
           
           ('a3','previousa','p(?|?) tgt2src? distortion table','4','34'),
           ('ahmm','previousa','p(?|?) tgt2src? distortion table from HMM','3','H'),
           ('n3','previousn','fertility table; Each line in this file is of the following format:'+
                'source_token_id p0 p1 p2 .... pn'+
                'where p0 is the probability that the source token has zero fertility;'+
                'p1, fertility one, ...., and n is the maximum possible fertility as defined in the program.',
                '4','34'),
           ('d3','previousd','src2tgt? distortion table','4','34'),
           ('d4','previousd4','Model 4 distortion table?','','4'),
           ('D4','previousd42','Model 4 distortion table?','','4')
          ]
        
        self.files = [
           # name, description, whenInput, whenOutput
           ('srcClasses','?','H4',''),
           ('tgtClasses','?','H4',''),
           ('srcVcb','source language vocab file','1H34',''),
           ('tgtVcb','target language vocab file','1H34',''),
           ('srcTgtSnt','Numerized sentence file with 3 lines per sentence pair: count, source sentence, target sentence','1H34',''),
           ('tgtSrcSnt','Numerized sentence file with 3 lines per sentence pair: count, target sentence, source sentence','1H34',''),
           ('srcTgtCooc', 'Cooccurrence matrix file with coocurrence counts of word pairs','1H34',''),
           ('tgtSrcCooc', 'Cooccurrence matrix file with coocurrence counts of word pairs','1H34',''),
            
           ('srcTgtAlignments','Viterbi alignments for the model', '', '1H34'),
           ('srcTgtGizacfg', 'Giza configuration file (for force alignment)', '', '1H34'),
           ]
        
        self.iterationParams = [
           # name, description, default, when
           ('model1iterations', 'Number of iterations when training model 1', '5', '1'),
           ('hmmiterations', 'Number of iterations when training hmm', '5', 'H'),
           ('model3iterations', 'Number of iterations when training model 3', '3', '3'),
           ('model4iterations', 'Number of iterations when training model 3', '3', '4'),
           ('model2iterations', 'Number of iterations when training model 2', '', ''),
           ('model5iterations', 'Number of iterations when training model 5', '', ''),
           ('model6iterations', 'Number of iterations when training model 6', '', ''),
            ]
        
        # TODO: Mine other parameters from MGIZA
        self.possibleParams = [('p0','p0 parameter', '0.999', '1234HA')]
        
    
    def getRequiredPaths(self):
        # Pass params to required paths?
        paths = ['mgiza']# 'mt-analyzers']
        return paths
    
    def appliesToModel(self, mode, when, params=None):
        if mode == 'A':
            models = '1H34'
        else:
            models = mode
            
        for model in models:
            if model in when:
                if params == None:
                    return True
                else:
                    if model == 'H':
                        paramName = 'hmmiterations'
                    else:
                        paramName = 'model'+model+'iterations'
                    iterations = params[paramName]
                    if not iterations:
                        n = 0
                    else:
                        n = int(iterations)
                    if n > 0:
                        return True
        return False

# Moses defaults
#    my %GizaDefaultOptions = 
#        (p0 => .999 ,
#         m1 => 5 , 
#         m2 => 0 , 
#         m3 => 3 , 
#         m4 => 3 , 
#         o => "giza" ,
#         nodumps => 1 ,
#         onlyaldumps => 1 ,
#         nsmooth => 4 , 
#         model1dumpfrequency => 1,
#         model4smoothfactor => 0.4 ,
#         t => $vcb_f,
#         s => $vcb_e,
#         c => $train,
#         CoocurrenceFile => "$dir/$f-$e.cooc",
#         o => "$dir/$f-$e");
#        $GizaDefaultOptions{m3} = 0;
#        $GizaDefaultOptions{m4} = 0;
#        $GizaDefaultOptions{hmmiterations} = 5;
#        $GizaDefaultOptions{hmmdumpfrequency} = 5;
#        $GizaDefaultOptions{nodumps} = 0;


    def getParamNames(self):
        params = []
        for (name, desc, default, when) in self.iterationParams:
            if self.appliesToModel(self.mode, when):
                params.append( (name, desc, default) )
        for (name, desc, default, when) in self.possibleParams:
            if self.appliesToModel(self.mode, when):
                params.append( (name, desc, default) ) 
        if not self.isChaski:
        	params.append( ('ncpus', 'Number of processor cores to use during word alignment', '2') )
        params.append( ('outputModelsForForceAlign','output penultimate models (which should be used when doing careful experimental comparisons with force alignment)') )
        return params

    def zeroIterations(self, params):
        for (name, desc, default, when) in self.iterationParams:
            if not self.appliesToModel(self.mode, when, params):
                params[name] = '0'
                
    def setDumpFrequency(self, params):
        # Since final model is always dumped, we can use the dump
        # frequency to make sure the second-to-last model
        # is always dumped, so that it can later
        # be used in Force Align
		if self.appliesToModel(self.mode, '4', params):
			params['model345dumpfrequency'] = str(int(params['model4iterations'])-1)
   		elif self.appliesToModel(self.mode, '3', params):
			params['model345dumpfrequency'] = str(int(params['model3iterations'])-1)
		elif self.appliesToModel(self.mode, 'H', params):
			params['hmmdumpfrequency'] = str(int(params['hmmiterations'])-1)
		elif self.appliesToModel(self.mode, '1', params):
			params['model1dumpfrequency'] = str(int(params['model1iterations'])-1)

    def getInputNames(self, params):
        inputs = []
         
        for (name, desc, whenIn, whenOut) in self.files:
            if ( (self.mode == 'A' and whenIn != '') or 
                self.appliesToModel(self.inputMode, whenIn, params)):
                    inputs.append( (name, desc) )
                
        for (name, gizaName, desc, whenIn, whenOut) in self.modelFiles:
            if self.appliesToModel(self.inputMode, whenIn, params):
                inputs.append( (name+'-final', desc) )
                
        return inputs

    def getOutputNames(self, params):
        outputs = []
        for (name, desc, whenIn, whenOut) in self.files:
            if self.appliesToModel(self.outputMode, whenOut, params):
                outputs.append( (name, desc) )
        for (name, gizaName, desc, whenIn, whenOut) in self.modelFiles:
            if self.appliesToModel(self.outputMode, whenOut, params):
                outputs.append( (name + '-final', desc + ' (For use in subsequent models)') )
        forForceAlign = self.isTrue(params['outputModelsForForceAlign'])
        if forForceAlign:
            outputs.append( (name + '-forForceAlign', desc + '(For use in Force Align)') )
        return outputs
    
    def setRestartLevel(self, params):
        if self.mode == '1' or self.mode == 'A':
            params['restart'] = '0'
        elif self.mode == 'H':
            params['restart'] = '4'
        elif self.mode == '3':
            params['restart'] = '7'
        elif self.mode == '4':
            params['restart'] = '10'
    
    def getCommands(self, params, inputs, outputs):
        Mgiza.zeroIterations(self, params)
        Mgiza.setDumpFrequency(self, params)
        Mgiza.setRestartLevel(self, params)
        params['log'] = '0'

        args = ' '.join('-%s %s'%(key, value) for key, value in params.iteritems())
        
        forForceAlign = self.isTrue(params['outputModelsForForceAlign'])

        # Add input model files from previous models
        for (name, gizaName, desc, whenIn, whenOut) in self.modelFiles:
            if self.appliesToModel(self.inputMode, whenIn, params):
                if gizaName:
                    inputFile = inputs[name+'-final']
                    args += ' -%s %s'%(gizaName, inputFile)
        
        commands = []
        
        # HMM alpha and beta require special names
        if self.appliesToModel(self.inputMode, '34', params):
            commands.append('ln -s `pwd`/%(hmmAlpha-final)s %(hhmm-final)s.alpha'%inputs)
            commands.append('ln -s `pwd`/%(hmmBeta-final)s %(hhmm-final)s.beta'%inputs)
        
        if 'srcClasses' in inputs:
            commands.append('ln -s `pwd`/%(srcClasses)s %(srcVcb)s.classes'%inputs)
        if 'tgtClasses' in inputs:
            commands.append('ln -s `pwd`/%(tgtClasses)s %(tgtVcb)s.classes'%inputs)
        commands.append('./src/mgiza -S %(srcVcb)s -T %(tgtVcb)s -C %(srcTgtSnt)s -coocurrencefile %(srcTgtCooc)s -outputfileprefix srctgt '%inputs + '%s | tee log'%args)

        # When do we merge alignments now?
        if self.outputMode == '1':            
            nIterations = int(params['model1iterations'])
            commands.append('./scripts/merge_alignment.py `ls srctgt.A1.'+str(nIterations)+'.part*` > %(srcTgtAlignments)s'%outputs)
        elif self.outputMode == 'H':
            nIterations = int(params['hmmiterations'])
            commands.append('./scripts/merge_alignment.py `ls srctgt.Ahmm.'+str(nIterations)+'.part*` > %(srcTgtAlignments)s'%outputs)
        elif self.outputMode == '3':
            nIterations = int(params['model3iterations'])
            commands.append('./scripts/merge_alignment.py `ls srctgt.A3.final.part*` > %(srcTgtAlignments)s'%outputs)
        elif self.outputMode == '4':
            nIterations = int(params['model4iterations'])
            # NOTE: Model 4 uses the same output template as Model 3
            commands.append('./scripts/merge_alignment.py `ls srctgt.A3.final.part*` > %(srcTgtAlignments)s'%outputs)
            
        # Symlink model files
        for (modelName, gizaName, desc, whenIn, whenOut) in self.modelFiles:
            if self.appliesToModel(self.outputMode, whenOut, params):
                if 'Alpha' in modelName or 'Beta' in modelName:
                    if 'Alpha' in modelName:
                        which = 'alpha'
                    else:
                        which = 'beta'
                    finalFile = outputs[modelName+'-final']
                    commands.append('ln -s `pwd`/srctgt.hhmm.%d.%s %s'%(nIterations, which, finalFile))

                    if forForceAlign:
                        forForceAlignFile = outputs[modelName+'-forForceAlign']
                        commands.append('ln -s `pwd`/srctgt.hhmm.%d.%s %s'%(nIterations-1, which, forForceAlignFile))

                else:
                    if forForceAlign:
                        forForceAlignFile = outputs[modelName+'-forForceAlign']
                        commands.append('ln -s `pwd`/srctgt.%s.%d %s'%(modelName, nIterations-1, forForceAlignFile))

                    finalFile = outputs[modelName+'-final']
                    if self.appliesToModel(self.outputMode, '34', params):
                        iterationName = 'final'
                    else:
                        iterationName = str(nIterations)
                    commands.append('ln -s `pwd`/srctgt.%s.%s %s'%(modelName, iterationName, finalFile))
        commands.append('ln -s $(pwd)/srctgt.gizacfg %(srcTgtGizacfg)s'%outputs)
      
        return commands

    ### TODO: Write preanalyzer that checks fertility against max sentence length ratio; fail if >

    def getPostAnalyzers(self, params, inputs, outputs):
        return [] # 'GrabGizaLog.py log srctgt.perp' ]
