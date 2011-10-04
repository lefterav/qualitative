'''
Created on 04 Οκτ 2011

@author: lefterav
'''

from orngSVM import SVMLearner

class SVMEasy(SVMLearner):
    '''
    classdocs
    '''

    def learnClassifier(self, examples):
        examples = continuize
        
        transformer=orange.DomainContinuizer()
        transformer.multinomialTreatment=orange.DomainContinuizer.NValues
        transformer.continuousTreatment=orange.DomainContinuizer.NormalizeBySpan
        transformer.classTreatment=orange.DomainContinuizer.Ignore
        newdomain=transformer(examples)
        newexamples=examples.translate(newdomain)
        #print newexamples[0]
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
    '''
        