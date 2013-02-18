'''
Created on Jan 23, 2013

@author: dupo
'''

import Orange
if __name__ == '__main__':
    voting = Orange.data.Table("trainset.tab")
    
    new_domain = Orange.data.Domain([a for a in voting.domain.variables if a.name != 'rank'], voting.domain['rank'])
    new_data = Orange.data.Table(new_domain, voting)
    
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
