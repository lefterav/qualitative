"""

@author: Eleftherios Avramidis
"""

#import pylab    
import Orange
from Orange.data import Instance
from Orange.data import Table
from Orange.classification import Classifier
from Orange.classification.rules import rule_to_string
from Orange.classification.rules import RuleLearner
from Orange.classification.svm import get_linear_svm_weights
from Orange import feature
from Orange.classification import logreg
from Orange.statistics import distribution

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
        
        if self.classifier.__class__.__name__ in ["NaiveClassifier", "CN2UnorderedClassifier"]:    
            self.discrete_features = [feature.Descriptor.make(feat.name,feat.var_type,[],feat.values,0) for feat in self.classifier.domain.features if isinstance(feat, feature.Discrete)]

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
        
        if self.classifier.__class__.__name__ in ["NaiveClassifier", "CN2UnorderedClassifier"]:
            orange_table = self.clean_discrete_features(orange_table)
        
        resultvector = []
        for instance in orange_table:
            value, distribution = self.classifier.__call__(instance, return_type)
            resultvector.append((value.value, distribution))
        return resultvector 
    
    
    def clean_discrete_features(self, orange_table):
        #kill instances that do not fit training data
        classifier_discrete_features = self.discrete_features
        print len(orange_table)
        i = 0
        k = 0
        for feat, status in classifier_discrete_features:
            classifier_feat_values = set([val for val in feat.values])
            table_feat_values = set([val for val in orange_table.domain[feat.name].values])
            missing_values = table_feat_values - classifier_feat_values
            
            if not missing_values:
                continue
            
            modus = distribution.Distribution(feat.name, orange_table).modus()
            instances = set(orange_table.filter_ref({feat.name:list(missing_values)}))
            for inst in instances:
                inst[feat.name] = modus
            
            i+=len(instances)
            k+=1    
        sys.stderr.write("Warning: Reset {} appearances of {} discrete attributes\n".format(i, k))
        return orange_table

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
        except:
            pass 
        
        try:
            rules = self.classifier.rules
            textfilename = "{}.rules.txt".format(basename)
            f = open(textfilename, "w")
            for r in rules:
                f.write("{}\n".format(rule_to_string(r)))             
            f.close()
            return 
        except:
            pass
        
        
        try:
            textfilename = "{}.tree.txt".format(basename)
            f = open(textfilename, "w")
            f.write(self.classifier.to_string("leaf", "node"))
            f.close()
            
            graphics_filename = "{}.tree.dot".format(basename)
            self.classifier.dot(graphics_filename, "leaf", "node")
        except:
            pass
            
        try:
            textfilename = "{}.dump.txt".format(basename)
            logreg.dump(self.classifier)
        except:
            pass    
                    
#    def _print_tree(self, x, fileobj):
#        if isinstance(x, Orange.classification.tree.TreeClassifier):
#            self._print_tree0(x.tree, 0, fileobj)
#        elif isinstance(x, Orange.classification.tree.Node):
#            self._print_tree0(x, 0, fileobj)
#        else:
#            raise TypeError, "invalid parameter"
#
#    def _print_tree0(self, node, level, fileobj):
#            if not node:
#                fileobj.write( " "*level + "<null node>\n")
#                return
#            if node.branch_selector:
#                node_desc = node.branch_selector.class_var.name
#                node_cont = node.distribution
#                fileobj.write("\\n" + "   "*level + "%s (%s)" % (node_desc, node_cont))
#                for i in range(len(node.branches)):
#                    fileobj.write("\\n" + "   "*level + ": %s" % node.branch_descriptions[i])
#                    self.print_tree0(node.branches[i], level+1)
#            else:
#                node_cont = node.distribution
#                major_class = node.node_classifier.default_value
#                fileobj.write("--> %s (%s)" % (major_class, node_cont))            
#            
            
#        if classifier_type == "SVMEasyLearner":
#            
#        elif 
            

