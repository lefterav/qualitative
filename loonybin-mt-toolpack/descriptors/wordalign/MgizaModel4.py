from loonybin import Tool
from Mgiza import Mgiza

class MgizaModel4(Mgiza):

    def __init__(self):
        Mgiza.__init__(self, '4', False)
    
    def getName(self):
        return 'Machine Translation/Word Alignment/MGIZA Local/MGIZA++ Model 4'
    
    def getDescription(self):
        return "Runs Multithreaded GIZA++ in a single direction for a parallel corpus. 'Source' and 'target' are referred to as x and y since alignment is usually run in both directions."

if __name__ == '__main__':
    import sys
    t = MgizaModel4()
    t.handle(sys.argv)
