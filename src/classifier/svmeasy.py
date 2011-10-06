'''

@author: lefterav
'''

from orngSVM import SVMLearner, SVMClassifierClassEasyWrapper
import orange
import orngWrap

class SVMEasy(SVMLearner):
    '''
    classdocs
    '''
    def __init__(self, **kwds):
        self.folds=4
        self.verbose=0
        SVMLearner.__init__(self, **kwds)
        self.learner = SVMLearner(**kwds)
        
    
    def continuize(self, examples):
        transformer=orange.DomainContinuizer()
        transformer.multinomialTreatment=orange.DomainContinuizer.NValues
        transformer.continuousTreatment=orange.DomainContinuizer.NormalizeBySpan
        transformer.classTreatment=orange.DomainContinuizer.Ignore
        newdomain=transformer(examples)
        newexamples=examples.translate(newdomain)
        return newdomain, newexamples

    def learnClassifier(self, examples):
        print "continuizing data"
        newdomain, newexamples = self.continuize(examples)
        newexamples.save("continuized_examples.tab")
        self.verbose = True
        print "tuning classifier"
        newdomain = newexamples.domain
        classifier = self.tuneClassifier(newexamples, newdomain, examples)
        return classifier
        
        #print newexamples[0]
    def tuneClassifier(self, newexamples, newdomain, examples):
        params={}
        parameters = []
        self.learner.normalization = False ## Normalization already done
        
        if self.svm_type in [1,4]:
            numOfNuValues=9
            if self.svm_type == SVMLearner.Nu_SVC:
                maxNu = max(self.maxNu(newexamples) - 1e-7, 0.0)
            else:
                maxNu = 1.0
            parameters.append(("nu", [i/10.0 for i in range(1, 9) if i/10.0 < maxNu] + [maxNu]))
        else:
            parameters.append(("C", [2**a for a in  range(-5,15,2)]))
        if self.kernel_type==2:
            parameters.append(("gamma", [2**a for a in range(-5,5,2)]+[0]))
        tunedLearner = orngWrap.TuneMParameters(object=self.learner, parameters=parameters, folds=self.folds)
        
        return SVMClassifierClassEasyWrapper(tunedLearner(newexamples, verbose=self.verbose), newdomain, examples)
    
        