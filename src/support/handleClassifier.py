# -*- coding: utf-8 -*-




'''
Created on Sep 1, 2010

@author: elav01

TODO: 
- find a way to save orange Data in XML format
- dep parser
- language model


'''

import sys, codecs, os, orange, orngTest, orngStat, orngTree,  xml.dom.minidom

from produceJudgmentFeatures import JudgedSet
from xml.dom.minidom import parse
from tempfile import mktemp

class OrangeData:

    
    def __init__ (self, dataObject, className="", desiredAttributes=[]):
        
        if isinstance ( dataObject , orange.ExampleTable ):
            self.data = dataObject
        else:
            
            #get the data in Orange file format
            fileData = self.__getOrangeFormat__(dataObject, className, desiredAttributes)
            
            #write the data in a temporary file
            tmpFileName = self.__writeTempFile__(fileData)
            
            #load the data
            self.data = orange.ExampleTable(tmpFileName)
            
            #get rid of the temp file
            os.unlink(tmpFileName)

        return None
    
    
    def getData(self):
        return self.data
    
    def printStatistics(self): 
        data=self.data
        # report on number of classes and attributes
        print "Classes:", len(data.domain.classVar.values) 
        print "Attributes:", len(data.domain.attributes), ",", 

        print "Classes:", len(data.domain.classVar.values)
        print "Attributes:", len(data.domain.attributes), ",",
        
        # count number of continuous and discrete attributes
        ncont=0; ndisc=0
        for a in data.domain.attributes:
            if a.varType == orange.VarTypes.Discrete:
                ndisc = ndisc + 1
            else:
                ncont = ncont + 1
        print ncont, "continuous,", ndisc, "discrete"
        
        # obtain class distribution
        c = [0] * len(data.domain.classVar.values)
        for e in data:
            c[int(e.getclass())] += 1
        print "Instances: ", len(data), "total",
        r = [0.] * len(c)
        for i in range(len(c)):
            r[i] = c[i]*100./len(data)
        for i in range(len(data.domain.classVar.values)):
            print ", %d(%4.1f%s) with class %s" % (c[i], r[i], '%', data.domain.classVar.values[i]),
        print 
        

        #missing values
        
        natt = len(data.domain.attributes)
        missing = [0.] * natt
        for i in data:
            for j in range(natt):
                if i[j].isSpecial():
                    missing[j] += 1
        missing = map(lambda x, l=len(data):x/l*100., missing)
        
        print "Missing values per attribute:"
        atts = data.domain.attributes
        for i in range(natt):
            print "  %5.1f%s %s" % (missing[i], '%', atts[i].name)
            
            
        #Domain distributions
        
        dist = orange.DomainDistributions(data)

        print "Average values and mean square errors:"
        for i in range(len(data.domain.attributes)):
            if data.domain.attributes[i].varType == orange.VarTypes.Continuous:
                print "%s, mean=%5.2f +- %5.2f" % \
                  (data.domain.attributes[i].name, dist[i].average(), dist[i].error())
        
        print "\nFrequencies for values of discrete attributes:"
        for i in range(len(data.domain.attributes)):
            a = data.domain.attributes[i]
            if a.varType == orange.VarTypes.Discrete:
                print "%s:" % a.name
                for j in range(len(a.values)):
                    print "  %s: %d" % (a.values[j], int(dist[i][j]))
        

    
    def __writeTempFile__(self, data):
        
        tmpFileName = mktemp(dir='.', suffix='.tab')
        file_object = codecs.open(tmpFileName, 'w', 'utf-8')
        file_object.write(data)
        file_object.close()  
        
        return tmpFileName
        
    
    def __getOrangeFormat__(self, xmlObject, className, desiredAttributes=[]):
        #first construct the lines for the declaration
        dataString = "" #text contained in the file to be written
        typeLine = "" #line for the type of the arguments
        classLine = "" #line for the definition of the class 
        if not desiredAttributes :
            attributeKeys = xmlObject.getXMLAttributes()
        else :
            desiredAttributes.append(className)
            attributeKeys = desiredAttributes
        
        for attributeKey in attributeKeys :
            dataString = dataString + attributeKey +"\t"
            typeLine = typeLine + "d\t"
            if className == attributeKey:
                classLine = classLine + "class"
            classLine = classLine + "\t"
        
        #add the class description in the end for all the three lines
        
        dataString = dataString + "\n"
        typeLine = typeLine + "\n"
        classLine = classLine + "\n"
        dataString = dataString + typeLine + classLine
        
        
        
        judgedCorpus = xmlObject.getOutput().getElementsByTagName('jcml')
        sentenceList = judgedCorpus[0].getElementsByTagName('judgedsentence')
        
        for xmlEntry in sentenceList:
            for attributeKey in attributeKeys:
                if attributeKey in xmlEntry.attributes.keys():
                    dataString = dataString + str(xmlEntry.attributes[attributeKey].value)
                #even if attribute value exists or not, we have to tab    
                dataString = dataString + "\t"
            #remove the last tab and replace it with a line break
            dataString = dataString + "\n"
        return dataString
    
    def splitData(self, percentage):
        size =  len (self.data)
        testSize = round (size * percentage) 
        
        indices = orange.MakeRandomIndices2(p0=testSize)
        indices.stratified = indices.Stratified 
        ind = indices(self.data)
        
        testSet = self.data.select(ind, 0)
        trainingSet = self.data.select(ind, 1)
        
        return [trainingSet, testSet] 
    
    def getBayesClassifier(self):
        return orange.BayesLearner(self.data)
    
    def getTreeLearner(self):
        return orngTree.TreeLearner(self.data, sameMajorityPruning=1, mForPruning=2)
     
    
    def crossValidation(self):
        
        data = self.data
        # set up the learners
        bayes = orange.BayesLearner()
        tree = orngTree.TreeLearner(mForPruning=2)
        bayes.name = "bayes"
        tree.name = "tree"
        
        l = orange.SVMLearner() 
        l.name = "SVM"
        
        l=orange.SVMLearner() 
        l.svm_type=orange.SVMLearner.Nu_SVC 
        l.nu=0.3 
        l.probability=True 
        
        learners = [bayes, tree, l]
        
        # compute accuracies on data
        
        
        res = orngTest.crossValidation(learners, data, folds=10)
        cm = orngStat.computeConfusionMatrices(res,
                classIndex=data.domain.classVar.values.index('-1'))
        
        stat = (('CA', 'CA(res)'),
                ('Sens', 'sens(cm)'),
                ('Spec', 'spec(cm)'),
                ('AUC', 'AUC(res)'),
                ('IS', 'IS(res)'),
                ('Brier', 'BrierScore(res)'),
                ('F1', 'F1(cm)'),
                ('F2', 'Falpha(cm, alpha=2.0)'),
                ('MCC', 'MCC(cm)'),
                ('sPi', 'scottsPi(cm)'),
                )

        scores = [eval("orngStat."+s[1]) for s in stat]
        print
        print "Learner  " + "".join(["%-7s" % s[0] for s in stat])
        for (i, l) in enumerate(learners):
            print "%-8s " % l.name + "".join(["%5.3f  " % s[i] for s in scores])
    
        return None
    
    def getSVM(self):
        l=orange.SVMLearner() 
        l.svm_type=orange.SVMLearner.Nu_SVC 
        l.nu=0.3 
        l.probability=True 
        return l(self.data) 
    
    
    
def accuracy(test_data, classifiers):
    correct = [0.0]*len(classifiers)
    for ex in test_data:
        for i in range(len(classifiers)):
            if classifiers[i](ex) == ex.getclass():
                correct[i] += 1
    for i in range(len(correct)):
        correct[i] = correct[i] / len(test_data)
    return correct
    
    
    
    
            
if __name__ == "__main__":
    if len(sys.argv) < 3 :
        print 'USAGE: %s JUDGMENTS_INPUT.pcml.xml JUDGMENTS_OUTPUΤ.pcml.xml ' % sys.argv[0]
    else:
        
        inputXML = JudgedSet(sys.argv[1],sys.argv[2])
        newData = OrangeData (inputXML, 'rank', ['src-toolong','src-long', 'langsrc', 'langtgt', 'testset'])
        
        newData.crossValidation()
        
        [trainingPart, testPart] = newData.splitData(0.1)
        trainingData = OrangeData(trainingPart)
        testData = OrangeData(testPart)
        
        
        bayes = trainingData.getBayesClassifier()
        tree = trainingData.getTreeLearner()
        svm = trainingData.getSVM()
        
        bayes.name = "bayes"
        tree.name = "tree"
        svm.name = "SVM"
        classifiers = [bayes, tree, svm]
        
        # compute accuracies
        acc = accuracy(testData.getData(), classifiers)
        print "Classification accuracies:"
        for i in range(len(classifiers)):
            print classifiers[i].name, acc[i]
        
        #newData.printStatistics()
        #print "Training Data"
        #trainingData.printStatistics()        
        
        
        
        
                
            
        
    
        
        
        