"""

@author: Eleftherios Avramidis
"""

import pylab    
import Orange
from Orange.data import Instance
from Orange.data import Table
from Orange.classification import Classifier


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
                
        classifier_type = self.__class__.__name__()
        
        
        if classifier_type in ["NaiveClassifier", ]:
            textfilename = "{}.txt".format(basename)
            f = open(textfilename)
            f.write(self.__str__())
            sepal_length, probabilities = zip(*self.conditional_distributions[0].items())
            p_setosa, p_versicolor, p_virginica = zip(*probabilities)
            
            imagefilename = "{}.png".format(basename)
            pylab.xlabel("sepal length")
            pylab.ylabel("probability")
            pylab.plot(sepal_length, p_setosa, label="setosa", linewidth=2)
            pylab.plot(sepal_length, p_versicolor, label="versicolor", linewidth=2)
            pylab.plot(sepal_length, p_virginica, label="virginica", linewidth=2)
            pylab.legend(loc="best")
            pylab.savefig(imagefilename)
        
            
        if classifier_type == "SVMEasyLearner":
            
        elif 
            

