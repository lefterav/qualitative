from loonybin import Tool
from Mgiza import Mgiza

class MgizaHmm(Mgiza):

    def __init__(self):
        Mgiza.__init__(self, 'H', False)
    
    def getName(self):
        return 'Machine Translation/Word Alignment/MGIZA Local/MGIZA++ HMM Model'
    
    def getDescription(self):
        return "Runs Multithreaded GIZA++ in a single direction for a parallel corpus. 'Source' and 'target' are referred to as x and y since alignment is usually run in both directions."

if __name__ == '__main__':
    import sys
    t = MgizaHmm()
    t.handle(sys.argv)
