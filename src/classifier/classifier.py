"""

@author: Eleftherios Avramidis
"""

import pylab    
import Orange
from Orange.data import Instance
from Orange.data import Table
from Orange.classification import Classifier
from Orange.classification.rules import rule_to_string
from Orange.classification.rules import RuleLearner
from Orange.classification.svm import get_linear_svm_weights
import sys

class OrangeClassifier(Classifier):
    """
    Basic wrapper to encapsulate common functions for all classifier subclasses
    @ivar classifier: the wrapped classifier
    @type classifier: L{Orange.classification.Classifier} 
    """
    def __new__(cls, wrapped):
        return Classifier.__new__(cls, name=wrapped.name)

    def __init__(self, wrapped):
        self.classifier = wrapped
        for name, val in wrapped.__dict__.items():
            self.__dict__[name] = val

    def __call__(self, example, what=Orange.core.GetBoth):
        example = Instance(self.classifier.domain, example)
        return self.classifier(example, what)
        
    def classify_orange_table(self, orange_table, return_type=Classifier.GetBoth):
    
        """
        Use the current classifier to classify the given orange table and return a vector (list) of the given values
        @param orange_table: An orange table with unclassified instances, which we need to classify
        @type orange_table: L{Orange.data.Table}
        @param return_type: Specifies whether the classification of each intance should return only the predicted value, only the predicted distribution or both (default),
        @type return_type: L{Orange.classification.Classifier.GetBoth} or L{Orange.classification.Classifier.GetProbabilities} or L{Orange.classification.Classifier.GetBoth)}
        @return: a list of the classification results, one list item per instance
        @rtype: [L{Orange.classification.Value}, ...] or [L{Orange.classification.Distribution}, ...] or [(L{Orange.classification.Value},L{Orange.classification.Distribution}), ...]    
        """
        #orange_table = Table()
        resultvector = []
        for instance in orange_table:
            value, distribution = self.classifier.__call__(instance, return_type)
            resultvector.append((value.value, distribution))
        return resultvector 
            

    def classify_dataset(self, dataset, return_type=Classifier.GetBoth):
        pass
    
    def classify_parallelsentence(self, parallelsentence, return_type=Classifier.GetBoth):
        pass
#    def __call__(self, data):
#        return self.classifier.__call__(data)
#        
#    def getFilteredLearner(self, n=5):
#        return orngFSS.FilteredLearner(self, filter=orngFSS.FilterBestNAtts(n), name='%s_filtered' % self.name)


    def print_content(self, basename="classifier"):
        """
        Depending on the type of the classifier, output its contents to an external file
        @param basename: the filename without extension of the classifier
        @type basename: string         
        """
                
        classifier_type = self.classifier.__class__.__name__
        
        print classifier_type
        
        if classifier_type in ["NaiveClassifier", ]:
#            textfilename = "{}.txt".format(basename)
#            f = open(textfilename, "w")
##            f.write(self.conditional_distributions[0].items()) 
#            f.close()
#            
#            sepal_length, probabilities = zip(*self.conditional_distributions[0].items())
#            print sepal_length
#            print probabilities
#            
#            p_setosa, p_versicolor = zip(*probabilities)
#            
#            imagefilename = "{}.png".format(basename)
#            pylab.xlabel("sepal length")
#            pylab.ylabel("probability")
#            pylab.plot(sepal_length, p_setosa, label="setosa", linewidth=2)
#            pylab.plot(sepal_length, p_versicolor, label="versicolor", linewidth=2)
##            pylab.plot(sepal_length, p_virginica, label="virginica", linewidth=2)
#            pylab.legend(loc="best")
#            pylab.savefig(imagefilename)
            pass
        
        #if we are talking about a rule learner, just print its rules out in the file
        try:        
            
            weights = get_linear_svm_weights(self.classifier)
            textfilename = "{}.weights.txt".format(basename)
            f = open(textfilename, "w")
            f.write("Fitted parameters: \nnu = {0}\ngamma = {1}\n\nWeights: \n".format(self.classifier.fitted_parameters[0], self.classifier.fitted_parameters[1]))
            for weight_name, weight_value in weights.iteritems():
                f.write("{0}\t{1}\n".format(weight_name, weight_value))           
            f.close()
        except AttributeError:
            pass 
        
        try:
            rules = self.classifier.rules
            textfilename = "{}.rules.txt".format(basename)
            f = open(textfilename, "w")
            for r in rules:
                f.write("{}\n".format(rule_to_string(r)))             
            f.close()
            return 
        except AttributeError:
            pass
        
        
            
            
            
#        if classifier_type == "SVMEasyLearner":
#            
#        elif 
            

