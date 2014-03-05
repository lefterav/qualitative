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
from Orange.classification.logreg import LibLinearLogRegLearner
from Orange.regression.pls import PLSRegressionLearner
from Orange.regression.lasso import LassoRegressionLearner
from Orange.evaluation.scoring import CA, Precision, Recall, F1, MCC
from Orange.evaluation.testing import cross_validation
from Orange.feature.scoring import Relief
import logging

DELIMITER = " % "
NEWLINE = " \\\\ \n"
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
    coefficients = {}
    evaluation = {}
    evaluation_metrics = [CA, Precision, Recall, F1, MCC]
    
    for class_name in error_category_names:    
        
        coefficients[class_name] = {}
        evaluation[class_name] = {}
        
        orangeconvertor = CElementTreeJcml2Orange(input_filename, 
                                         class_name, 
                                         desired_attributes, 
                                         meta_attributes, 
                                         output_file,
                                         compact_mode=True)
            
        print "\n\n[[[[", class_name, "]]]]\n"
        table = Table(output_file)
        learner = LibLinearLogRegLearner()
        model = learner(table)
        
        #store classifier somewhere for future use        
        textfilename = "{}.logreg.dump.txt".format(class_name)
        f = open(textfilename, 'w')
        f.write(dump(model))
        f.close()
        
        #store weights into results table
        coefficients_filename = "{}.logreg.coeff.tex".format(class_name)
        f = open(coefficients_filename, 'w')
        for feat, weight in zip(model.domain.features, model.weights[0]):
            f.write("{} {} {} {}".format(feat.name, DELIMITER, weight, NEWLINE))
            coefficients[class_name][feat.name] = weight
        
        #perform cross validation to see quality of model
        cv = cross_validation([learner], table, 10)                
        for evaluation_metric in evaluation_metrics:
            evaluation_result = evaluation_metric(cv)
            evaluation[class_name][evaluation_metric.name] = evaluation_result[0]
        f.close()

    #header
    evaluation_filename = "{}.logreg.eval.tex".format(class_name)
    f = open(evaluation_filename, 'w')
    f.write(" {} {} {}".format(DELIMITER, DELIMITER.join(evaluation.keys()), NEWLINE))
    #content
    for class_name in evaluation.keys():         
        values = [evaluation[class_name][evaluation_metric.name] for evaluation_metric in evaluation_metrics]
        f.write("{} {} {} {}".format(class_name, DELIMITER, DELIMITER.join(values), NEWLINE))
    f.close()
    
    