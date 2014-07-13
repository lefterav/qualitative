'''
Draft script one-for-all. Gets one argument from commandline
which contains sentences and error analysis

it prints feature correlation and results of logistic regression

Created on 17 Apr 2013

@author: Eleftherios Avramidis
'''

import sys, logging
import glob, os
from dataprocessor.ce.cejcml2orange import CElementTreeJcml2Orange
from dataprocessor.sax.utils import join_jcml
from Orange.data import Table, Domain
from Orange.regression.lasso import LassoRegressionLearner
from Orange.classification.logreg import LogRegLearner, dump
from Orange.classification.logreg import LibLinearLogRegLearner
from Orange.regression.pls import PLSRegressionLearner
from Orange.regression.lasso import LassoRegressionLearner
from Orange.evaluation.scoring import CA, Precision, Recall, F1, MCC, RMSE, MAE, R2
from Orange.evaluation.testing import cross_validation
from Orange.feature.scoring import Relief

sth = logging.StreamHandler()
sth.setLevel(logging.INFO)


#table format specified with next variables
DELIMITER = ","
NEWLINE = "\n"

error_category_names = [
                    #'iHper',
                    #'iRper',
                    
                    'arLexErr',
                    'aMissErr',
                    'aExtErr',
                    'arRer',
                    #'hLexErr',
                   
                    #'hRer',  
                    #'biHper',
                    #'biRper',
                    #'rbRer',
                    #'hbRer',
                    #'bmissErr',
                    #'bextErr',
                    #'rbLexErr',
                    #'hbLexErr'
                    ]

excluded_error_category_names = ['iHper',
                    'iRper',
                    'hLexErr',
                    'hRer',  
                    'biHper',
                    'biRper',
                    'rbRer',
                    'hbRer',
                    'bmissErr',
                    'bextErr',
                    'rbLexErr',
                    'hbLexErr',
                    'rLexErr',
                    'missErr',
                    'extErr',
                    'rRer',

                
                    ]
                    
metric_names = ['wer',
                    'hper', 
                    'rper',]

general_meta_attributes = ['uid', 'langsrc', 'langtgt']
                    


#add prefix
error_category_names = ['tgt-1_{}'.format(name) for name in error_category_names]
excluded_error_category_names = ['tgt-1_{}'.format(name) for name in excluded_error_category_names]
metric_names = ['tgt-1_{}'.format(name) for name in metric_names]

general_meta_attributes.extend(metric_names)

meta_attributes = []
meta_attributes.extend(error_category_names)
meta_attributes.extend(excluded_error_category_names)
meta_attributes.extend(general_meta_attributes)

classes = error_category_names


print "meta_attributes =", meta_attributes
        
desired_attributes = []


if __name__ == '__main__':


    #input_filename_pattern = sys.argv[1]
    # glob.glob(input_filename_pattern)
    input_filenames = sys.argv[1:]
    
    print "Input filenames:", input_filenames
    
    input_filename = "train.jcml"
    join_jcml(input_filenames, input_filename)
    
    output_file = "orange.tab"
    coefficients = {}
    evaluation = {}
    evaluation_metrics = [RMSE, MAE, R2]
    
    for class_name in classes:    
        logging.info(class_name)
        coefficients[class_name] = {}
        evaluation[class_name] = {}
        
        logging.info("converting data")
        orangeconvertor = CElementTreeJcml2Orange(input_filename, 
                                         class_name, 
                                         desired_attributes, 
                                         meta_attributes, 
                                         output_file,
                                         compact_mode=True,
                                         nullimputation=True,
                                         allowmissingclass=False,
                                         remove_infinite=True,
                                         class_type='c')
        orangeconvertor.convert()
        logging.info(class_name)
        table = Table(output_file)
        learner = LassoRegressionLearner()
        model = learner(table)
        
        #store classifier somewhere for future use
        logging.info("store classifier somewhere for future use")
        textfilename = "{}.logreg.dump.txt".format(class_name)
        f = open(textfilename, 'w')
        f.write(str(model))
        f.close()
        print "done"
        #store weights into results table
        #logging.info("store weights into results table")
        #coefficients_filename = "{}.logreg.coeff.csv".format(class_name)
        #f = open(coefficients_filename, 'w')
        #for feat, weight in zip(model.domain.features, model.weights[0]):
        #    f.write("{} {} {} {}".format(feat.name, DELIMITER, weight, NEWLINE))
        #    coefficients[class_name][feat.name] = weight
        
        #perform cross validation to see quality of model
        logging.info("perform cross validation to see quality of model")
        cv = cross_validation([learner], table, 10)                
        for evaluation_metric in evaluation_metrics:
            evaluation_result = evaluation_metric(cv)
            evaluation[class_name][evaluation_metric.__name__] = evaluation_result[0]
        f.close()
    #header
    logging.info("writing accuracy results")
    evaluation_filename = "logreg.eval.csv"
    f = open(evaluation_filename, 'w')
    f.write(" {} {} {}".format(DELIMITER, DELIMITER.join([m.__name__ for m in evaluation_metrics]), NEWLINE))
    #content
    for class_name in evaluation.keys():   
        values = []
        for evaluation_metric in evaluation_metrics:
            try:
                value = round(evaluation[class_name][evaluation_metric.__name__],3)           
            except TypeError:
                value = evaluation[class_name][evaluation_metric.__name__]
            values.append(str(value))
            
        f.write("{} {} {} {}".format(class_name, DELIMITER, DELIMITER.join(values), NEWLINE))
    f.close()
    
    
