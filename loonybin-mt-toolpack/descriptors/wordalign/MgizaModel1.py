from loonybin import Tool
from Mgiza import Mgiza

class MgizaModel1(Mgiza):

    def __init__(self):
        Mgiza.__init__(self, '1', False)
    
    def getName(self):
        return 'Machine Translation/Word Alignment/MGIZA Local/MGIZA++ Model 1'
    
    def getDescription(self):
        return "Runs Multithreaded GIZA++ in a single direction for a parallel corpus. 'Source' and 'target' are referred to as x and y since alignment is usually run in both directions."

if __name__ == '__main__':
    import sys
    t = MgizaModel1()
    t.handle(sys.argv)
