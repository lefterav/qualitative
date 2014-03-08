'''
Draft script one-for-all. Gets one argument from commandline
which contains sentences and error analysis

it prints feature correlation and results of logistic regression

Created on 17 Apr 2013

@author: Eleftherios Avramidis
'''

from io_utils.sax.cejcml2orange import CElementTreeJcml2Orange
import sys
from Orange.data import Table, Domain
from Orange.classification.logreg import LogRegLearner, dump
from Orange.evaluation.scoring import CA
from Orange.evaluation.testing import cross_validation
from Orange.feature.scoring import Relief

error_category_names = [
                    'iHper',
                    'iRper',
                    'missErr',
                    'extErr',
                    'rLexErr',
                    'hLexErr',
                    'rRer',
                    'hRer',  
                    'biHper',
                    'biRper',
                    'rbRer',
                    'hbRer',
                    'bmissErr',
                    'bextErr',
                    'rbLexErr',
                    'hbLexErr']


metric_names = ['wer',
                    'hper', 
                    'rper',]

general_meta_attributes = ['uid', 'langsrc', 'langtgt']


#add prefix
error_category_names = ['tgt-1_{}'.format(name) for name in error_category_names]
metric_names = ['tgt-1_{}'.format(name) for name in metric_names]

general_meta_attributes.extend(metric_names)

meta_attributes = []
meta_attributes.extend(error_category_names)
meta_attributes.extend(general_meta_attributes)

print meta_attributes
        
desired_attributes = []


def print_featureselection(table, class_name):
    new_domain = Domain([a for a in table.domain.variables if a.name != class_name], table.domain[class_name])
    new_data = Table(new_domain, table)
    
    def print_best_100(ma):
        for m in ma[:100]:
            print "%5.3f %s" % (m[1], m[0])
    

    
    print 'Relief:\n'
    meas = Relief(k=20, m=50)
    mr = [(a.name, meas(a, new_data)) for a in new_data.domain.attributes]
    mr.sort(key=lambda x: -x[1]) #sort decreasingly by the score
    print_best_100(mr)



if __name__ == '__main__':


    
    input_filename = sys.argv[1]
    output_file = "/tmp/orange.tab"
    for class_name in error_category_names:    
        orangeconvertor = CElementTreeJcml2Orange(input_filename, 
                                         class_name, 
                                         desired_attributes, 
                                         meta_attributes, 
                                         output_file,
                                         compact_mode=True)
        orangeconvertor.convert()
        table = Table(output_file)
    
        print "\n\n[[[[", class_name, "]]]]\n"
        #print_featureselection(table,class_name)

        learner = LogRegLearner(stepwise_lr=True)
        model = learner(table)

        textfilename = "{}.logreg.dump.txt".format(class_name)
        f = open(textfilename, 'w')
        f.write(dump(model))
        f.close()
        

        cv = cross_validation([learner], table, 10)        
        ca = CA(cv)
        print "CA [{}] = {}".format(class_name, ca[0])

