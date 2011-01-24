from loonybin import Tool

class Align(Tool):
    
    def getName(self):
        return 'Machine Translation/Visualization/Visualize Alignments (Meteor X-Ray)'
    
    def getDescription(self):
        return "Visualize METEOR alignment matrices"
    
    def getRequiredPaths(self):
        return ['meteor']

    def getParamNames(self):
        return [ ('numAlignments', 'Max number of alignments to visualize (recommend 1000)') ]
    
    def getInputNames(self, params):
        return [ ('alignment', 'METEOR alignment file') ]

    def getOutputNames(self, params):
        return [ ('alignment.tex','Alignment tex file'),
                 ('alignment.pdf','Alignment PDF file')]

    def getPreAnalyzers(self, params, inputs):
        return [ ]
    
    def getCommands(self, params, inputs, outputs):
        return [ 'python ./xray/visualize_alignments.py' \
          + ' %(alignment)s' % inputs \
          + ' tmp' \
          + ' %(numAlignments)s' % params \
          + ' && mv tmp.pdf %(alignment.pdf)s' % outputs
          + ' && mv tmp.tex %(alignment.tex)s' % outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = Align()
    t.handle(sys.argv)
