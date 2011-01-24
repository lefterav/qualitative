from loonybin import Tool

import sys
scriptDir = sys.path[0]
sys.path.append(scriptDir)
from Mgiza import Mgiza

class MgizaAll(Mgiza):

    def __init__(self):
        Mgiza.__init__(self, 'A', False)
    
    def getName(self):
        return 'Machine Translation/Word Alignment/MGIZA Local/MGIZA++ All Models at Once'
    
    def getDescription(self):
        return "Runs Multithreaded GIZA++ in a single direction for a parallel corpus. 'Source' and 'target' are referred to as x and y since alignment is usually run in both directions."

if __name__ == '__main__':
    import sys
    t = MgizaAll()
    t.handle(sys.argv)

