'''
Created on Jan 23, 2013

@author: Eleftherios Avramidis
'''

import Orange

import sys
if __name__ == '__main__':
    table = Orange.data.Table(sys.argv[1])
    classname = sys.argv[2]
    
    new_domain = Orange.data.Domain([a for a in table.domain.variables if a.name != classname], table.domain[classname])
    new_data = Orange.data.Table(new_domain, table)
    
    def print_best_100(ma):
        for m in ma[:100]:
            print "%5.3f %s" % (m[1], m[0])
    

    
    print 'Relief:\n'
    meas = Orange.feature.scoring.Relief(k=20, m=50)
    mr = [ (a.name, meas(a, new_data)) for a in new_data.domain.attributes]
    mr.sort(key=lambda x: -x[1]) #sort decreasingly by the score
    print_best_100(mr)
    
    print "InfoGain\n"
    
    meas = Orange.feature.scoring.InfoGain()
    mr = [ (a.name, meas(a, new_data)) for a in new_data.domain.attributes]
    mr.sort(key=lambda x: -x[1]) #sort decreasingly by the score
    print_best_100(mr)
