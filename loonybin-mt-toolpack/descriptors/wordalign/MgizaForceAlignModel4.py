from loonybin import Tool

class MgizaForceAlignModel4(Tool):

    def getName(self):
        return 'Machine Translation/Word Alignment/MGIZA Local/MGIZA++ Force Align Model 4'
    
    def getDescription(self):
        return """
        Force alignment of unseen data usng MGIZA++ with existing model 4 parameters
        """
    
    def getRequiredPaths(self):
        return ['mgiza']

    def getParamNames(self):
        return []

    def getInputNames(self, params):
        return [ ('srcCorpus', 'Source (foreign) corpus, same tokenization as training data'),
                 ('tgtCorpus', 'Target (native) corpus, same tokenization as training data'),
                 ('srcVcb', 'Source vocabulary'),
                 ('tgtVcb', 'Target vocabulary'),
                 ('srcClasses', 'Source word classes'),
                 ('tgtClasses', 'Target word classes'),
                 ('srcTgtGizacfg', 'MGIZA configuration source-target'),
                 ('t3-final', 'From previous MGIZA run'),
                 ('a3-final', 'From previous MGIZA run'),
                 ('d3-final', 'From previous MGIZA run'),
                 ('n3-final', 'From previous MGIZA run'),
                 ('d4-final', 'From previous MGIZA run'),
                 ('D4-final', 'From previous MGIZA run'),
                 ]

    def getOutputNames(self, params):
        return [ ('srcTgtAlignments','MGIZA A3.final'),
                 ('srcTgtSnt','Sentence file source-target'),
                 ('tgtSrcSnt','Sentence file target-source'),
                 ('srcVcbx','Augmented source vocabulary'),
                 ('tgtVcbx','Augmented target vocabulary'),
                 ('srcTgtCooc', 'Co-occurrences (source-target)'),
                 ('t3-final', 'MGIZA output'),
                 ('a3-final', 'MGIZA output'),
                 ('d3-final', 'MGIZA output'),
                 ('n3-final', 'MGIZA output'),
                 ('d4-final', 'MGIZA output'),
                 ('D4-final', 'MGIZA output'),
                 ]
    
    def getCommands(self, params, inputs, outputs):
        # Regardless of what executable help messages call inputs/outputs, the
        # order is always source (foreign) then target (native)
        return [
            # Create snt files for input and augmented vcb files
            ('./scripts/plain2snt-hasvcb.py %(srcVcb)s %(tgtVcb)s %(srcCorpus)s %(tgtCorpus)s'%inputs +
             ' %(srcTgtSnt)s %(tgtSrcSnt)s %(srcVcbx)s %(tgtVcbx)s'%outputs),
            # Link vcbx and word class files so MGIZA can find them
            ('ln -s %(srcVcbx)s'%outputs + ' src.vcbx'),
            ('ln -s %(tgtVcbx)s'%outputs + ' tgt.vcbx'),
            ('ln -s %(srcClasses)s'%inputs + ' src.vcbx.classes'%outputs),
            ('ln -s %(tgtClasses)s'%inputs + ' tgt.vcbx.classes'%outputs),
            # Generate cooc files
            ('./src/snt2cooc %(srcTgtCooc)s %(srcVcbx)s %(tgtVcbx)s %(srcTgtSnt)s'%outputs),
            # Run MGIZA source-target
            ('./src/mgiza %(srcTgtGizacfg)s'%inputs + ' -c %(srcTgtSnt)s'%outputs +
             ' -o src-tgt -s src.vcbx -t tgt.vcbx -m1 0 -m2 0 -mh 0'%outputs +
             ' -coocurrence %(srcTgtCooc)s -restart 11'%outputs +
             ' -previoust %(t3-final)s -previousa %(a3-final)s -previousd %(d3-final)s'%inputs +
             ' -previousn %(n3-final)s -previousd4 %(d4-final)s -previousd42 %(D4-final)s'%inputs +
             ' -m3 0 -m4 1 -outputpath \'\''),
            # Merge alignments
            ('./scripts/merge_alignment.py src-tgt.A3.final.part* > %(srcTgtAlignments)s'%outputs),
            # Link files
            ('ln -s $(pwd)/src-tgt.t3.final %(t3-final)s'%outputs),
            ('ln -s $(pwd)/src-tgt.a3.final %(a3-final)s'%outputs),
            ('ln -s $(pwd)/src-tgt.d3.final %(d3-final)s'%outputs),
            ('ln -s $(pwd)/src-tgt.n3.final %(n3-final)s'%outputs),
            ('ln -s $(pwd)/src-tgt.d4.final %(d4-final)s'%outputs),
            ('ln -s $(pwd)/src-tgt.D4.final %(D4-final)s'%outputs),
            ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return []

if __name__ == '__main__':
    import sys
    t = MgizaForceAlignModel4()
    t.handle(sys.argv)
