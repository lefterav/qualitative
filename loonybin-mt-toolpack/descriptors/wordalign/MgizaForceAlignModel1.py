from loonybin import Tool
from MgizaForceAlign import MgizaForceAlign

class MgizaForceAlignModel1(MgizaForceAlign):

    def __init__(self):
        Mgiza('1')
    
    def getName(self):
        return 'Machine Translation/Word Alignment/MGIZA++ Force Align Model 1'
    
    def getDescription(self):
        return "Runs Multithreaded GIZA++ in a single direction for a parallel corpus. 'Source' and 'target' are referred to as x and y since alignment is usually run in both directions."

if __name__ == '__main__':
    import sys
    t = MgizaForceAlignModel1()
    t.handle(sys.argv)
