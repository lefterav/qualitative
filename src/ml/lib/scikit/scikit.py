'''
Created on 25 Mar 2014

@author: Eleftherios Avramidis
'''
import numpy as np
from ml.learner import Regressor
from learn_model import set_learning_method, set_selection_method, scale_datasets_crossvalidation
from sklearn import cross_validation
from sklearn.metrics import make_scorer
import logging as log

from sklearn.externals.joblib import Parallel, delayed
from sklearn.base import is_classifier, clone
import numbers 
from sklearn.cross_validation import is_classifier, check_cv, _PartitionIterator, KFold



def dataset_to_instances(dataset, 
                         class_name,
                         desired_parallel_attributes = [],
                         desired_source_attributes = [],
                         desired_target_attributes = [],
                         meta_attributes = [],
                         class_level="target"):
    
    att_table = []
    class_vector = []

    f=open("data.tab", 'w')
    c=open("class.tab", 'w')

    for parallelsentence in dataset.get_parallelsentences():
        for translation in parallelsentence.get_translations():
            #log.debug("Parallelsentence {}".format(parallelsentence.get_attribute("id")))
            #get the class value
            if class_name:
                if class_level=="target":
                    class_vector.append(float(translation.get_attribute(class_name)))
                    c.write("{}\n".format(translation.get_attribute(class_name)))
                elif class_level=="parallel":
                    class_vector.append(float(parallelsentence.get_attribute(class_name)))
                
            #get all features in a row and then in a table
            att_row = []
            log.debug("Target attributes: {}".format(len(desired_target_attributes)))
            for att_name in desired_target_attributes:
                if att_name != "":
                        try:
                            att_value = translation.get_attribute(att_name)
                            att_value = att_value.replace("inf", "99999999")
                            att_value = att_value.replace("nan", "0")                                
                            att_row.append(float(att_value))
                            f.write(str(att_value))
                            f.write("\t")
                        except AttributeError:
                            log.debug("target attribute {} could not be found in sentence with id={}, replacing with 0".format(att_name, parallelsentence.get_attribute("id")))
                            att_row.append(0)
                            
            log.debug("Parallel attributes: {}".format(len(desired_parallel_attributes)))                        
            for att_name in desired_parallel_attributes:
                if att_name != "":
                    try:
                        att_value = parallelsentence.get_attribute(att_name)
                        att_row.append(float(att_value))
                    except AttributeError:
                        log.debug("parallel attribute {} could not be found in sentence with id={}, replacing with 0".format(att_name, parallelsentence.get_attribute("id")))
                        att_row.append(0)
            
            log.debug("Source attributes: {}".format(len(desired_source_attributes)))
            for att_name in desired_source_attributes:
                if att_name != "":
                    try:
                        att_value = parallelsentence.get_source().get_attribute(att_name)
                        att_value = att_value.replace("inf", "99999999")
                        att_value = att_value.replace("nan", "0") 
                        att_row.append(float(att_value))
                        f.write(str(att_value))
                        f.write("\t")
                    except AttributeError:
                        log.debug("source attribute {} could not be found in sentence with id={}, replacing with 0".format(att_name, parallelsentence.get_attribute("id")))
                        att_row.append(0)
        
            log.debug("id: {}, row length: {}".format(parallelsentence.get_attribute("id"), len(att_row)))
            f.write("\n")
            att_table.append(att_row)

    numpy_att_table = np.asarray(att_table)
    #log.debug("numpy_att_table: {}".format(numpy_att_table))
    numpy_class_vector = np.asarray(class_vector)

    if len(numpy_att_table.shape) != 2:
        log.info("Shape of loaded data: {}".format(numpy_att_table.shape))
        raise IOError("the training dataset must be in the format of a matrix with M lines and N columns.")
        
    #if numpy_att_table.shape[0] != numpy_class_vector.shape[0]:
    #    raise IOError("the number of instances in the train features file does not match the number of references given.")
    
    f.close()
    c.close()
    
    
    return numpy_att_table, numpy_class_vector




        
        
class SkRegressor(Regressor):
    def __init__(self, config=None):
        self.config = config
        
    
    def load_training_dataset(self, dataset,
                         class_name,
                         desired_parallel_attributes = [],
                         desired_source_attributes = [],
                         desired_target_attributes = [],
                         meta_attributes = [],
                         scale=True):
        
        self.X_train, self.y_train = dataset_to_instances(dataset, 
                         class_name,
                         desired_parallel_attributes,
                         desired_source_attributes,
                         desired_target_attributes,
                         meta_attributes)
        
        if scale:
            self.X_train = scale_datasets_crossvalidation(self.X_train)
        
    
    def feature_selection(self, threshold=.25):
        config = self.config
        # sets the selection method
        transformer = set_selection_method(config, threshold)
    
        # if the system is configured to run feature selection
        # runs it and modifies the datasets to the new dimensions
        if transformer is not None:
            log.info("Running feature selection %s" % str(transformer))
            log.info("X_train dimensions before fit_transform(): %s,%s" % self.X_train.shape)
            log.info("y_train dimensions before fit_transform(): %s" % self.y_train.shape)
            
            X_train = transformer.fit_transform(self.X_train, self.y_train)
            
            log.info("Dimensions after fit_transform(): %s,%s" % X_train.shape)
        
        
    def set_learning_method(self):
        self.estimator, self.scorers = set_learning_method(self.config, self.X_train, self.y_train)
    
    
    def cross_validate_start(self, cv=10, n_jobs=15, scorer=None, fixed_folds=None):
        if not scorer:
            scorer = make_scorer(self.scorers[0][1]) 
        log.info("Running cross validator with %s" % str(self.estimator))
        if not fixed_folds:
            cv = KFold(len(self.y_train), n_folds=cv, indices=True)
            print "test instances:\n", [fold[1] for fold in cv]
        else:
            log.info("proceeding with fixed folds provided")
            cv = FixedFolds(len(self.y_train), fixed_folds)
            
        scores = cross_validation.cross_val_score(self.estimator, self.X_train, self.y_train, cv=cv, n_jobs=n_jobs, scoring=scorer)
        return scores
#        return scores

    def train_test(self, X_test, blah, dummy, roundup=None):
        self.estimator.fit(self.X_train, self.y_train)
        X_test = scale_datasets_crossvalidation(X_test)
        return self.estimator.predict(X_test)
        
        


class FixedFolds(_PartitionIterator):
    def __init__(self, n, existing_test_indices):
        self.test_folds = existing_test_indices
        self.indices=True
        self.n = n 

    def _iter_test_indices(self):
        for test_folds in self.test_folds:
            yield test_folds
        
    def __repr__(self):
        return '{}.{} (n={})'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            len(self.test_folds)
        )
    
    def __len__(self):
        return len(self.test_folds)
        
        
def ter_train_test(estimators, Xs_train, ys_train, X_test, denominator, verbose, fit_params, roundup=False):
    estimations = []

    

    for estimator in estimators:
        X_train = Xs_train[estimator]
        y_train = ys_train[estimator]
        estimator.fit(X_train, y_train)
        y_predict = estimator.predict(X_test)
        if roundup:
            y_predict = np.rint(y_predict)
        estimations.append(y_predict)
        
    all_estimations = np.column_stack(estimations)
    log.info("all_estimations.shape = {}".format(all_estimations.shape))
    
    sum_estimations = np.sum(all_estimations, axis=1)
    log.info("sum_estimations.shape = {}".format(sum_estimations.shape))
#    log.info("tokens.shape = {}".format(X[:,0].shape))
            
    ter = np.divide(sum_estimations, denominator)
    
    for i in range(len(ter)):
        log.info("ter{} = {:.3g} + {:.3g} + {:.3g} + {:.3g} / {} = {:.3g}".format(i, estimations[0][i], estimations[1][i], estimations[2][i], estimations[3][i], X_test[i,0], ter[i]))    
    return ter       
                
def ter_cross_validate_fold(estimators, X_dic, y_dic, denominator, tergold, scorer, train, test, verbose, fit_params, roundup=False):
    estimations = []
    denom_test = denominator[test]
    tergold_test = tergold[test]
    for estimator in estimators:
        X = X_dic[estimator]
        y = y_dic[estimator]
        X_train = [X[idx] for idx in train]
        X_test = [X[idx] for idx in test]
        y_train = y[train]
        y_test = y[test]
        estimator.fit(X_train, y_train)
        y_predict = estimator.predict(X_test)
        if roundup:
            y_predict = np.rint(y_predict)
        estimations.append(y_predict)
        
    all_estimations = np.column_stack(estimations)
    log.info("all_estimations.shape = {}".format(all_estimations.shape))
    
    sum_estimations = np.sum(all_estimations, axis=1)
    log.info("sum_estimations.shape = {}".format(sum_estimations.shape))
#    log.info("tokens.shape = {}".format(X[:,0].shape))
            
    ter = np.divide(sum_estimations, denom_test)
    for i in range (0,10):
        log.info("ter{} = {:.3g} + {:.3g} + {:.3g} + {:.3g} / {} = {:.3g} [{:.3g}]".format(i, estimations[0][i], estimations[1][i], estimations[2][i], estimations[3][i], X[i,0], ter[i], tergold_test[i]))
    
#    print ter.shape,
#    print y_test.shape,
    
#    print ter
#    print tergold_test
    score = scorer(ter, tergold_test)
    return score


class TerRegressor(SkRegressor):
    def __init__(self, config, skregressors, tergold):
        self.tergold = tergold
        self.config = config
        self.estimators = [skregressor.estimator for skregressor in skregressors]
        self.scorers = skregressors[0].scorers
        self.X_train = {}
        self.y_train = {}
        for skregressor in skregressors:
            self.X_train[skregressor.estimator] = skregressor.X_train
            self.y_train[skregressor.estimator] = skregressor.y_train
        self.size = len(self.y_train[skregressors[0].estimator])
        self.denominator = self.X_train[skregressors[0].estimator][:,0]
   
    def cross_validate_start(self, cv=10, n_jobs=15, verbose=0, pre_dispatch='2*n_jobs', fit_params=None, fixed_folds=None, roundup=False):
        if not fixed_folds:
            cvfolds = KFold(self.size, n_folds=cv, indices=True)
        else:
            log.info("proceeding with fixed folds provided")
            cvfolds = FixedFolds(self.size, fixed_folds)
        parallel = Parallel(n_jobs=n_jobs, verbose=verbose,
                        pre_dispatch=pre_dispatch)
        scorer = self.scorers[0][1]
        scores = parallel(
            delayed(ter_cross_validate_fold)(self.estimators, self.X_train, self.y_train, self.denominator, self.tergold, scorer, train, test, verbose, fit_params, roundup)
        for train, test in cvfolds)
        scores = np.array(scores)
        return scores
    
    def train_test(self, X_test, verbose, fit_params, roundup=False):
        X_test = scale_datasets_crossvalidation(X_test)
        return ter_train_test(self.estimators, self.X_train, self.y_train, X_test, X_test[:,0],  verbose, fit_params, roundup=False)

    
        
        
        

from sklearn.svm import SVR

class TerSVR(SVR):
    def __init__(self, estimators):
        self.estimators = estimators
        
    def fit(self, X, y):
#        for estimator, X, y in zip(self.estimators, Xs[:-1], ys[:-1]):
        for estimator in self.estimators:
            estimator.fit(X,y)
        return self 
    
    def predict(self, X):
        estimations = []
#        print "X: ", X
#        for estimator, X in zip(self.estimators, Xs[:-1]):
        for estimator in self.estimators:       
            ex = estimator.predict(X) 
#            print ex
            estimation = np.rint(ex)
#            print estimation
            log.info("estimation.shape = {}".format(estimation.shape))
            estimations.append(estimation)
            #log.info("Estimate: {}".format(estimate))

        #each estimation on numpy row
        all_estimations = np.column_stack(estimations)
        log.info("all_estimations.shape = {}".format(all_estimations.shape))
        
        sum_estimations = np.sum(all_estimations, axis=1)
        log.info("sum_estimations.shape = {}".format(sum_estimations.shape))
        log.info("tokens.shape = {}".format(X[:,0].shape))
                
        ter = np.divide(sum_estimations, X[:,0])
        for i in range (0,10):
            log.info("ter{} = {:.3g} + {:.3g} + {:.3g} + {:.3g} / {} = {:.3g}".format(i, estimations[0][i], estimations[1][i], estimations[2][i], estimations[3][i], X[i,0], ter[i]))
        
#        print "x: ", [x[0] for x in X]
#        print "Ter: ", ter
        return ter

        
    
        
   
            
            
        
    
