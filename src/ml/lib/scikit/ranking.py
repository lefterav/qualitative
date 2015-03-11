'''
Utilize the scikit machine learning library for ranking
Created on Sep 24, 2014

@author: Eleftherios Avramidis
'''

#our modules
from ml.lib.scikit.sklearn_utils import assert_number, assert_string
from ml.ranking import Ranker
from ml.lib.scikit.learn_model import optimize_model
from evaluation_measures import mean_absolute_error, root_mean_squared_error
from sentence.pairwiseparallelsentenceset import CompactPairwiseParallelSentenceSet
from dataprocessor.ce.cejcml import CEJcmlReader
from sklearn_utils import scale_datasets_crossvalidation

#generic
import numpy as np
import logging as log
from collections import OrderedDict

#scikit classifiers
from sklearn.svm import SVC, LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.linear_model.randomized_l1 import RandomizedLasso
from sklearn.ensemble.forest import ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.lda import LDA
from sklearn.qda import QDA

#scikit others
from sklearn.svm.classes import SVR
from sklearn.linear_model.coordinate_descent import LassoCV
from sklearn.linear_model.least_angle import LassoLars, LassoLarsCV
from sklearn.preprocessing.imputation import Imputer
from sklearn import preprocessing
from sklearn.preprocessing.data import StandardScaler
from sklearn.metrics.metrics import mean_squared_error, f1_score, precision_score, recall_score

def dataset_to_instances(filename, 
                         attribute_set=None,
                         class_name=None,
                         reader=CEJcmlReader,  
                         tempdir = "/tmp",
                         output_filename=None,
                         default_value = 0,
                         replace_infinite=False,
                         imputer=True,
                         **kwargs):
    """
    Receive a dataset filename and convert it into a memory table for the Orange machine learning
    toolkit. Since we need support for big data sets and optimal memory usage, the best way
    seems to create a temporary external tab separated file and load it directly with the Orange
    loader, which is implemented in C. This way no double object instances need to be on memory
    during conversion time.
    @param attribute_set: A description of the attributes we want to be included in the data table
    @type attribute_set: L{AttributeSet}
    @param class_name: The name of the class (label) for the machine learning task
    @type class_name: C{str}
    @param reader: A class which is able to read from external files. This give the possibility to 
    change the default reading behaviour (incremental XML reader) and read from other types of data files
    @type reader: L{DataReader} 
    @param tempdir: the temporary directory where the incremental file is written. Due to the
    increased I/O access, this is suggested to be in a storage unit that is locally connected to the
    computer that does the processsing, and not e.g. via NFS.
    @type tempdir: C{str}
    @param ouput_filename: specify here a full path if a copy of the Orange tab separated file needs to be
    retained (e.g. for debugging purposes)
    @type output_filename: C{str}
    @return An Orange Table object
    @rtype: C{Table}
    """
    
    
    
    #initialize the class that will take over the reading from the file
    dataset = reader(filename, compact=True, 
                     all_general=True,
                     all_target=True)
    
    features = None
    labels = None
    
    #iterate over all parallel sentences provided by the data reader
    i = 0

    for parallelsentence in dataset.get_parallelsentences():
        i += 1
        log.debug("Sentence {}".format(i))
        vectors = parallelsentence.get_vectors(attribute_set, 
                                               class_name=class_name, 
                                               default_value=default_value,
                                               replace_infinite=replace_infinite,
                                               )
        
        #every parallelsentence has many instances
        featurevectors = []
        class_values = []
        
        #create a temporary python array for the new vectors
        for featurevector, class_value in vectors:
            #log.debug("Featurevector {} before converting to numpy {}".format(len(featurevector), featurevector))
            featurevector = np.array(featurevector)
            #log.debug("Featurevector {} after converting to numpy {}".format(featurevector.shape, featurevector))
            featurevectors.append(featurevector)
            class_values.append(class_value)
        
        log.debug("Featurevectors {} before converting to numpy {}".format(len(featurevectors), featurevectors))

        #convert to numpy
        newfeatures = np.array(featurevectors)
        newlabels = np.array(class_values)
        #log.debug("Featurevectors {} after converting to numpy {}".format(newfeatures.shape, newfeatures))
        
        #append them to existing vectors if there are
        try:
            features = np.concatenate((features, newfeatures), axis=0)
            labels = np.concatenate((labels, newlabels), axis=0)
            #log.debug("Featurevectors {} after concatenating: {}".format(features.shape, features))
        except ValueError:
            #or initialize the total vectors 
            #log.debug("Initializing featurevectors")
            features = newfeatures
            labels = newlabels
        
    #print features 
    #print labels 
    if not imputer: #run imputer only if enabled (default)
        return np.nan_to_num(features)
    else:
        imp = Imputer(missing_values='NaN', strategy='mean', axis=0, verbose=2)
        try:
            impfeatures = imp.fit_transform(features)
        except ValueError as exc:
            #catch errors with illegal values (e.g. strings)
            log.warning("Exception trying to run scikit imputation: {}".format(exc))
        #show size for debugging purposes
        #log.debug("Featurevectors {} after imputation: {}".format(impfeatures.shape, features))i

        #we don't want shape to change, so if this happens, then just replace nans with zero and infinites
        if impfeatures.shape == features.shape:
            features = impfeatures
        else:
            log.warning("Using numpy NaN substitution")
            features = np.nan_to_num(features)
    return features, labels

def parallelsentence_to_instance(parallelsentence, attribute_set):
    vectors = parallelsentence.get_vectors(attribute_set, bidirectional_pairs=False, default_value=-500, replace_infinite=True, replace_nan=False)
    #every parallelsentence has many instances
    featurevectors = []
    
    #create a temporary python array for the new vectors
    for featurevector, _ in vectors:
        featurevectors.append(np.array(featurevector))
        
    #convert to numpy
    return featurevectors
    

class SkLearner:
    def initialize(self):
        ranker = eval(self.name)
        self.learner = self.name
        self.scaler = None
   
    def initialize_feature_selector(self, feature_selector=None, feature_selection_params={}, feature_selection_threshold=.25):
        p = feature_selection_params
        transformer = None
        if feature_selector == "RandomizedLasso":
            transformer = RandomizedLasso(alpha=p.setdefault("alpha", "aic"), 
                                    scaling=p.setdefault("scaling", .5), 
                                    sample_fraction=p.setdefault('sample_fraction', .75), 
                                    n_resampling=p.setdefault('n_resampling', 200),
                                    selection_threshold=feature_selection_threshold, 
                                    fit_intercept=p.setdefault('fit_intercept', True), 
                                    # TODO: set verbosity according to global level
                                    verbose=True, 
                                    normalize=p.setdefault('normalize', True), 
                                    max_iter=p.setdefault('max_iter', 500), 
                                    n_jobs=p.setdefault('n_jobs', 1))
        elif feature_selector == "ExtraTreesClassifier":
            transformer = ExtraTreesClassifier(n_estimators=p.get('n_estimators', 10),
                                     max_depth=p.get('max_depth', None),
                                     min_samples_split=p.get('min_samples_split', 1),
                                     min_samples_leaf=p.get('min_samples_leaf', 1),
                                     min_density=p.get('min_density', 1),
                                     max_features=p.get('max_features', 'auto'),
                                     bootstrap=p.get('bootstrap', False),
                                     compute_importances=p.get('compute_importances', True),
                                     n_jobs=p.get('n_jobs', 1),
                                     random_state=p.get('random_state', None),
                                     # TODO: set verbosity according to global level
                                     verbose=True)
        elif feature_selector == "GP":
            #TODO: add here Gaussian Processes
            transformer = None
        return transformer
    
    
    def run_feature_selection(self, feature_selector, data, labels):
        if feature_selector:
            log.info("scikit: Running feature selection {}".format(feature_selector))
            
            log.info("scikit: data dimensions before fit_transform(): {}".format(data.shape))
            log.info("scikit: labels dimensions before fit_transform(): {}".format(labels.shape))
            feature_selector.fit_transform(data, labels)
            
            log.info("scikit: Dimensions after fit_transform(): %s,%s" % data.shape)
        return data
    
    
    
    def initialize_learning_method(self, learner, data, labels, 
                                   learning_params={}, 
                                   optimize=True,
                                   optimization_params={},
                                   scorers=['mae', 'rmse']):
                                    
        o = optimization_params
        tune_params = self.initialize_optimization_params(optimization_params)        
        method_name = learner
        
        if method_name == "SVR":
            if optimize:
                estimator = optimize_model(SVR(), data, labels, 
                                          tune_params, 
                                          scorers, 
                                          o.setdefault("cv", 5),
                                          o.setdefault("verbose", True),
                                          o.setdefault("n_jobs", 1))
            else:
                estimator = SVR()
        
        elif method_name == "SVC":
            if optimize:
                estimator = optimize_model(SVC(probability=True), data, labels,
                                           tune_params,
                                           scorers,
                                           o.setdefault('cv', 5),
                                           o.setdefault('verbose', True),
                                           o.setdefault('n_jobs', 1))
                
            else:
                estimator = SVC(C=learning_params.setdefault('C', 1.0),
                                kernel=learning_params.setdefault('kernel', 'rbf'), 
                                degree=learning_params.setdefault('degree', 3),
                                gamma=learning_params.setdefault('gamma', 0.0),
                                coef0=learning_params.setdefault('coef0', 0.0),
                                tol=learning_params.setdefault('tol', 1e-3),
                                verbose=learning_params.setdefault('verbose', False))

                    
        elif method_name == "LassoCV":
            estimator = LassoCV(eps=learning_params.setdefault('eps', 1e-3),
                                n_alphas=learning_params.setdefault('n_alphas', 100),
                                normalize=learning_params.setdefault('normalize', False),
                                precompute=learning_params.setdefault('precompute', 'auto'),
                                max_iter=learning_params.setdefault('max_iter', 1000),
                                tol=learning_params.setdefault('tol', 1e-4),
                                cv=learning_params.setdefault('cv', 10),
                                verbose=False)

        
        elif method_name == "LassoLars":
            if optimize:
                estimator = optimize_model(LassoLars(), data, labels, 
                                          tune_params,
                                          scorers,
                                          o.get("cv", 5),
                                          o.get("verbose", True),
                                          o.get("n_jobs", 1))
                
            else:
                estimator = LassoLars(alpha=learning_params.setdefault('alpha', 1.0),
                                      fit_intercept=learning_params.setdefault('fit_intercept', True),
                                      verbose=learning_params.setdefault('verbose', False),
                                      normalize=learning_params.setdefault('normalize', True),
                                      max_iter=learning_params.setdefault('max_iter', 500),
                                      fit_path=learning_params.setdefault('fit_path', True))
        
            
        elif method_name == "LassoLarsCV":
            estimator = LassoLarsCV(max_iter=learning_params.setdefault('max_iter', 500),
                                        normalize=learning_params.setdefault('normalize', True),
                                        max_n_alphas=learning_params.setdefault('max_n_alphas', 1000),
                                        n_jobs=learning_params.setdefault('n_jobs', 1),
                                        cv=learning_params.setdefault('cv', 10),
                                        verbose=False)

        else:
            estimator_obj = eval(method_name)
            estimator = estimator_obj()
        return estimator, scorers
                
    
    def initialize_optimization_params(self, optimization_params):
        params = {}
        log.debug("Optimization params = {}".format(optimization_params))
        for key, item in optimization_params.iteritems():
            # checks if the item is a list with numbers (ignores cv and n_jobs params)
            if isinstance(item, list) and (len(item) == 3) and assert_number(item):
                # create linear space for each parameter to be tuned
                params[key] = np.linspace(item[0], item[1], num=item[2], endpoint=True)
                
            elif isinstance(item, list) and assert_string(item):
                params[key] = item
        
        return params    
    

    
    
class SkRanker(Ranker, SkLearner):
    '''
    Basic ranker wrapping scikit-learn functions
    '''
    
    def train(self, dataset_filename, 
              scale=True, 
              feature_selector=None, 
              feature_selection_params={},
              feature_selection_threshold=.25, 
              learning_params={}, 
              optimize=True, 
              optimization_params={}, 
              scorers=['f1_score'],
              attribute_set=None,
              class_name=None,
              **kwargs):
        
        data, labels = dataset_to_instances(dataset_filename, attribute_set, class_name,  **kwargs)
        learner = self.learner
        
        #the class must remember the attribute_set and the class_name in order to reproduce the vectors
        self.attribute_set = attribute_set
        self.class_name = class_name

 
        #scale data to the mean
        if scale:
            log.info("Scaling datasets...")
            log.debug("Data shape before scaling: {}".format(data.shape))
            self.scaler = StandardScaler()
            data = self.scaler.fit_transform(data)
        
        #avoid any NaNs and Infs that may have occurred due to the scaling
        data = np.nan_to_num(data)
        log.debug("Mean: {} , Std: {}".format(self.scaler.mean_, self.scaler.std_))
        
        #feature selection
        feature_selector = self.initialize_feature_selector(feature_selector, feature_selection_params, feature_selection_threshold)
        data = self.run_feature_selection(feature_selector, data, labels) 
        
        #initialize learning method and scoring functions and optimize
        self.classifier, self.scorers = self.initialize_learning_method(learner, data, labels, learning_params, optimize, optimization_params, scorers)

        log.debug("Data shape before fitting: {}".format(data.shape))

        self.classifier.fit(data, labels)
        self.fit = True
    
    def get_model_description(self):
        params = {}
        
        if self.scaler:
            params = self.scaler.get_params(deep=True)
        try: #these are for SVC
            if self.classifier.kernel == "rbf":
                params["gamma"] = self.classifier.gamma
                params["C"] = self.classifier.C
                for i, n_support in enumerate(self.classifier.n_support_):
                    params["n_{}".format(i)] = n_support
                log.info(len(self.classifier.dual_coef_))
                return params
            elif self.classifier.kernel == "linear":
                coefficients = self.classifier.coef_
                att_coefficients = {}
                for attname, coeff in zip(self.attribute_set.get_names_pairwise(), coefficients[0]):
                    att_coefficients[attname] = coeff
                return att_coefficients
        except AttributeError:
            pass
        try: #adaboost etc
            params = self.classifier.get_params()
            numeric_params = OrderedDict()
            for key, value in params.iteritems():
                try:
                    value = float(value)
                except ValueError:
                    continue
                numeric_params[key] = value
            return numeric_params
        except:
            pass
        return {}
    
    
    def get_ranked_sentence(self, parallelsentence, critical_attribute="rank_predicted", 
                            new_rank_name="rank_hard", 
                            del_orig_class_att=False, 
                            bidirectional_pairs=False, 
                            ties=True,
                            reconstruct='hard'):
        """
        """
        
        #de-compose multiranked sentence into pairwise comparisons
        pairwise_parallelsentences = parallelsentence.get_pairwise_parallelsentences(bidirectional_pairs=bidirectional_pairs,
                                                                                     class_name=self.class_name,
                                                                                     ties=ties)        
        if len(parallelsentence.get_translations()) == 1:
            log.warning("Parallelsentence has only one target sentence")
            parallelsentence.tgt[0].add_attribute(new_rank_name, 1)
            return parallelsentence, {}
        elif len(parallelsentence.get_translations()) == 0:
            return parallelsentence, {}
        #list that will hold the pairwise parallel sentences including the classifier's decision
        classified_pairwise_parallelsentences = []
        resultvector = []
        
        for pairwise_parallelsentence in pairwise_parallelsentences:
            #convert pairwise parallel sentence into an orange instance
            instance = parallelsentence_to_instance(pairwise_parallelsentence, attribute_set=self.attribute_set)
            #scale data instance to mean, based on trained scaler
            if self.scaler:
                try:
                    instance = np.nan_to_num(instance)
                    instance = self.scaler.transform(instance)
                except ValueError as e:
                    log.error("Could not transform instance: {}".format(instance))
                    raise ValueError(e)
            log.debug('Instance = {}'.format(instance)) 
            #make sure no NaN or inf appears in the instance
            instance = np.nan_to_num(instance)
            #run classifier for this instance
            predicted_value = self.classifier.predict(instance)
            try:
                distribution = dict(zip(self.classifier.classes_, self.classifier.predict_proba(instance)[0]))
            except AttributeError: 
                #if classifier does not support per-class probability (e.g. LinearSVC) assign 0.5
                distribution = dict([(cl, 0.5) for cl in self.classifier.classes_])
            log.debug("Distribution: {}".format(distribution))
            log.debug("Predicted value: {}".format(predicted_value))
            #even if we have a binary classifier, it may be that it cannot decide between two classes
            #for us, this means a tie
            if not bidirectional_pairs and distribution and len(distribution)==2 and float(distribution[1])==0.5:
                predicted_value = 0
                distribution[predicted_value] = 0.5
                
            log.debug("{}, {}, {}".format(pairwise_parallelsentence.get_system_names(), predicted_value, distribution))
            
            
            #gather several metadata from the classification, which may be needed 
            resultvector.append({'systems' : pairwise_parallelsentence.get_system_names(),
                                 'value' : predicted_value,
                                 'distribution': distribution,
                                 'confidence': distribution[int(predicted_value)],
                                 'instance' : instance})
            
            #add the new predicted ranks as attributes of the new pairwise sentence
            pairwise_parallelsentence.add_attributes({"rank_predicted":predicted_value,
                                                       "prob_-1":distribution[-1],
                                                       "prob_1":distribution[1]
                                                       })
            
            classified_pairwise_parallelsentences.append(pairwise_parallelsentence)

        
        #gather all classified pairwise comparisons of into one parallel sentence again
        sentenceset = CompactPairwiseParallelSentenceSet(classified_pairwise_parallelsentences)
        if reconstruct == 'hard':
            ranked_sentence = sentenceset.get_multiranked_sentence(critical_attribute=critical_attribute, 
                                                               new_rank_name=new_rank_name, 
                                                               del_orig_class_att=del_orig_class_att)
        else:
            attribute1 = "prob_-1"
            attribute2 = "prob_1"
            try:
                ranked_sentence = sentenceset.get_multiranked_sentence_with_soft_ranks(attribute1, attribute2, critical_attribute, new_rank_name)
            except:
                raise ValueError("Sentenceset {} from {} caused exception".format(classified_pairwise_parallelsentences, parallelsentence))
        return ranked_sentence, resultvector

if __name__ == '__main__':
    import sys, logging
    from sentence.parallelsentence import AttributeSet
    filename = sys.argv[1]
    output_filename = sys.argv[2]
    attribute_set = AttributeSet()
    attribute_set.target_attribute_names = ['cross-meteor_score', 'lm_unk', 'l_tokens', 'berkeley-n', 'parse-VP', 'berkley-loglikelihood']
    class_name = "ref-rgbF"

    loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                                    datefmt='%m-%d %H:%M')


    dataset_to_instances(filename, 
                         attribute_set,
                         class_name,
                         output_filename=output_filename,
                         )

