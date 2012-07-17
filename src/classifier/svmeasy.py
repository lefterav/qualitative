'''

@author: lefterav
'''

from Orange.classification.svm import SVMLearner #, SVMClassifierClassEasyWrapper
from Orange.optimization import TuneMParameters
from Orange.core import DomainContinuizer


class SVMEasyLearner(SVMLearner):
    '''
    classdocs
    '''
    def __init__(self, **kwds):
        self.folds=4
        self.verbose=True
#        SVMLearner.__init__(self, **kwds)
        self.learner = SVMLearner(**kwds)
        try: 
            self.multinomialTreatment = eval(kwds["multinomialTreatment"])
        except:
            self.multinomialTreatment = DomainContinuizer.NValues
        try:
            self.continuousTreatment = eval(kwds["continuousTreatment"])
        except:
            self.continuousTreatment = DomainContinuizer.NormalizeBySpan
        try:            
            self.classTreatment = eval(kwds["classTreatment"])
        except:
            self.classTreatment = DomainContinuizer.Ignore

    def __call__(self, examples, weight=0):        
        print "continuizing data"
        newdomain, newexamples = self.continuize(examples)
        newexamples.save("continuized_examples.tab")
        self.verbose = True
        print "tuning classifier"
        classifier, fittedParameters = self.tuneClassifier(newexamples, newdomain, examples)
        
        paramfile = open("svm.params", 'w')
        print fittedParameters
        for param in fittedParameters:
            paramfile.write(str(param))
            paramfile.write("\n")
        
        paramfile.close()
        return classifier
        
    def continuize(self, examples):
        transformer=DomainContinuizer()
        #transformer.multinomialTreatment=orange.DomainContinuizer.NValues
        #transformer.continuousTreatment=orange.DomainContinuizer.NormalizeBySpan
        transformer.multinomialTreatment = self.multinomialTreatment
        transformer.continuousTreatment = self.continuousTreatment
        transformer.classTreatment = self.classTreatment
        #transformer.classTreatment = orange.DomainContinuizer.Ignore
        newdomain = transformer(examples)
        newexamples = examples.translate(newdomain)
        return newdomain, newexamples
        #print newexamples[0]
        
    def tuneClassifier(self, newexamples, newdomain, examples):
        params={}
        parameters = []
        self.learner.normalization = False ## Normalization already done
        
        if self.svm_type in [1,4]:
            numOfNuValues=9
            if self.svm_type == self.SVMLearner.Nu_SVC:
                maxNu = max(self.maxNu(newexamples) - 1e-7, 0.0)
            else:
                maxNu = 1.0
            parameters.append(("nu", [i/10.0 for i in range(1, 9) if i/10.0 < maxNu] + [maxNu]))
        else:
            parameters.append(("C", [2**a for a in  range(-5,15,2)]))
        if self.kernel_type==2:
            parameters.append(("gamma", [2**a for a in range(-5,5,2)]+[0]))
        tunedLearner = TuneMParameters(object=self.learner, parameters=parameters, folds=self.folds)
        appliedTunedLearner = tunedLearner(newexamples, verbose=self.verbose)
             
        #return SVMClassifierClassEasyWrapper(appliedTunedLearner, newdomain, examples), appliedTunedLearner.fittedParameters
        return appliedTunedLearner, appliedTunedLearner.fittedParameters


            
        
#examples = orange.ExampleTable("/home/lefterav/workspace/TaraXUscripts/src/training-attset1.100.tab")
#svmlearner = SVMEasy(examples)
#
#testexamples = orange.ExampleTable("/home/lefterav/workspace/TaraXUscripts/src/training-attset2.tab")
#print svmlearner(testexamples[1])

#objectfile = open("/tmp/svmeasy.pickle", 'w')
#pickle.dump(svmlearner, objectfile)
#objectfile.close()
#
#objectfile = open("/tmp/svmeasy.pickle", 'r')
#recovered_svmlearner = pickle.load(objectfile)
#objectfile.close()
#print recovered_svmlearner(testexamples[1])



        
