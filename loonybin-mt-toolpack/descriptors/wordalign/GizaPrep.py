from loonybin import Tool

class GIZA(Tool):
    
    def getName(self):
        return 'Machine Translation/Word Alignment/MGIZA Local/MGIZA++ Prep'
    
    def getDescription(self):
        return """
        Uses plain2snt to convert parallel text into a numeric vocabulary and snt files with words replaced by their vocabulary indices.
        """
    
    def getRequiredPaths(self):
        return ['mgiza', 'mt-analyzers']

    def getParamNames(self):
        return []

    def getInputNames(self, params):
        return [ ('srcCorpusIn', 'foreign side of parallel corpus, one sentence per line'),
                 ('tgtCorpusIn', '"English" side of parallel corpus, one sentence per line') ]

    def getOutputNames(self, params):
        return [ ('srcVcb','source language vocab file'),
                 ('tgtVcb','target language vocab file'),
                 ('srcTgtSnt','Numerized sentence file with 3 lines per sentence pair: count, source sentence, target sentence'),
                 ('tgtSrcSnt','Numerized sentence file with 3 lines per sentence pair: count, target sentence, source sentence'),
                 ('srcTgtCooc', 'Cooccurrence matrix file with coocurrence counts of word pairs'),
                 ('tgtSrcCooc', 'Cooccurrence matrix file with coocurrence counts of word pairs') ]
    
    def getCommands(self, params, inputs, outputs):
        return [
            ('ln -s %(srcCorpusIn)s s'%inputs),
            ('ln -s %(tgtCorpusIn)s t'%inputs),
            ('./src/plain2snt s t'),
            ('./src/snt2cooc %(srcTgtCooc)s s.vcb t.vcb s_t.snt'%outputs),
            ('./src/snt2cooc %(tgtSrcCooc)s t.vcb s.vcb t_s.snt'%outputs),
            ('mv s.vcb '%inputs + '%(srcVcb)s'%outputs),
            ('mv t.vcb '%inputs + '%(tgtVcb)s'%outputs),
            ('mv s_t.snt '%inputs + '%(srcTgtSnt)s'%outputs),
            ('mv t_s.snt '%inputs + '%(tgtSrcSnt)s'%outputs),
            ]

    def getPostAnalyzers(self, params, inputs, outputs):
        #cmds = [ ('AnalyzeGizaSntVcb.sh %(srcVcb)s %(tgtVcb)s %(srcTgtSnt)s %(tgtSrcSnt)s'%outputs) ]
        # TODO: get name of loonFile and step
        #for key in ['src.VcbLines', 'tgt.VcbLines', 'src-tgt.SntLines', 'tgt-src.SntLines']:
        #    cmds.append('loon-assert-geq %s -c 1'%key)
        return []

if __name__ == '__main__':
    import sys
    t = GIZA()
    t.handle(sys.argv)
