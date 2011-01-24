from loonybin import Tool

class Viz(Tool):
    
    def getName(self):
        return 'Machine Translation/Visualization/Visualize System Differences (Meteor X-RAY)'
    
    def getDescription(self):
        return "Visualize system differences according to a Meteor alignment"
    
    def getRequiredPaths(self):
        return ['meteor']

    def getParamNames(self):
        return [ ('lang', 'two-letter language code') ]
    
    def getInputNames(self, params):
        return [ ('refs', 'METEOR alignment file'),
                 ('sysA', 'x'),
                 ('sysB','x')]

    def getOutputNames(self, params):
        return [ ('mx-align.pdf','Meteor X-Ray PDF showing how system hypotheses align to references'),
                 ('mx-score.pdf','Meteor X-Ray PDF showing charts of how hypotheses score in various categories')]

    def getPreAnalyzers(self, params, inputs):
        return [ ]
    
    def getCommands(self, params, inputs, outputs):
        return [ 'java -XX:+UseCompressedOops -Xmx2G -jar meteor-1.2.jar %(sysA)s %(refs)s'%inputs +
                 ' -l %(lang)s -f sys1 -normalize -keepPunctuation -writeAlignments'%params,

                 'java -XX:+UseCompressedOops -Xmx2G -jar meteor-1.2.jar %(sysB)s %(refs)s'%inputs +
                 ' -l %(lang)s -f sys2 -normalize -keepPunctuation -writeAlignments'%params,

                 'python ./xray/xray.py -c -l System-1,System2 sys1-align.out sys2-align.out',

                 'mv mx-align.pdf %s'%(outputs['mx-align.pdf']),
                 'mv mx-score.pdf %s'%(outputs['mx-score.pdf']) ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

    def isInspector(self):
        return True

if __name__ == '__main__':
    import sys
    t = Viz()
    t.handle(sys.argv)
