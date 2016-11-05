#!/usr/bin/python
# -*- coding: utf-8 -*-


"""

@author: Eleftherios Avramidis
"""

import codecs
import os
import sys
import orange, orngTest, orngStat, orngTree  
from tempfile import mktemp
from sentence.dataset import DataSet
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
import sentence 
from copy import deepcopy
from xml.sax import make_parser



class AttributesReader:
    
    def __init__(self, file, class_name, meta_attributes, desired_attributes = [] ):
        """
        @param out: file object to receive processed changes
        @type out: file
        @param feature_generators: list of feature generators to be applied
        @type feature_generators: list
        """
        
        self.attribute_names = set()
        self.tgt_count = 0
        self.file = file
        self.desired_attributes = desired_attributes
        self.meta_attributes = meta_attributes
    
    def startElement(self, name, attrs = []):
        """
        Signals the start of an element (simplesentence or parallelsentence)
        @param name: the name of the element
        @type name: str 
        @param attrs: of the element type as a string and the attrs parameter holds an object of the Attributes interface containing the attributes of the element.
        @type attrs: Attributes
        """
            
        for att_name in attrs.getNames():
            if name == self.TAG_SRC:
                att_name = "src_%s" % att_name
                self.tgt_count = 0
            elif name == self.TAG_TGT:
                self.tgt_count += 1
                att_name = "tgt%d_%s" % att_name
            elif name == self.TAG_REF:
                att_name = "ref_%s" % att_name
            self.attribute_names.add(att_name)
    
    def endDocument(self):
        
                #first construct the lines for the declaration
        line_1 = "" #line for the name of the arguments
        line_2 = "" #line for the type of the arguments
        line_3 = "" #line for the definition of the class 
        print "Getting attributes"
        desired_attributes = self.desired_attributes
        meta_attributes = self.meta_attributes
        
        print self.attribute_names
        if self.desired_attributes == []:
            desired_attributes = self.attribute_names
        
        #if no desired attribute define, get all of them
        #if not desired_attributes:
        #    desired_attributes =  attribute_names
        
        print "Constructing file"
        #prepare heading
        for attribute_name in self.attribute_names :
            #line 1 holds just the names
            line_1 = "%s%s\t" % (line_1, attribute_name)
                        
            #TODO: find a way to define continuous and discrete arg
            #line 2 holds the class type
            if attribute_name == self.class_name:
                line_2 = "%sd\t" % line_2
            elif attribute_name in desired_attributes and attribute_name not in meta_attributes:
                #line_2 += "%s\t" % desired_attributes[attribute_name]
                line_2 = "%sc\t" % line_2

            else:
                line_2 = "%sd\t" % line_2

            
            #line 3 defines the class and the metadata
            if attribute_name == self.class_name:
                line_3 = line_3 + "c"
            elif attribute_name not in desired_attributes or attribute_name in meta_attributes:
                line_3 = line_3 + "m"
            line_3 = line_3 + "\t"
        
        #src
        line_2 += "string\t"
        line_3 += "m\t"
        line_1 += "src\t"
        #target
        i=0
        for i in range (1, self.tgt_count):
            i+=1
            line_2 = "%sstring\t" % line_2
            line_3 = "%sm\t" % line_3
            line_1 = "%stgt-%d\t" % (line_1, i)
        #ref 
        line_2 += "string\t"
        line_3 += "m\t"
        line_1 += "ref\t"
        
        #break the line in the end
        line_1 = line_1 + "\n"
        line_2 = line_2 + "\n"
        line_3 = line_3 + "\n"
        output = line_1 + line_2 + line_3
        self.file.write(output)
        
class SentenceReader:
    
    def __init__(self):
        from dataprocessor.input.xliffreader import XliffReader
    def startElement(self, name, atts = []):
        if name == self.TAG_SENT:
            pass
    

class OrangeProcessor:
    """
        Handles the conversion of the generic data objects to a format handled by Orange library
    """
    
    def __init__ (self, dataSet, class_name="", desired_attributes=[], meta_attributes=[], keep_temp=False):
        if isinstance ( dataSet , orange.ExampleTable ):
            self.data = dataSet
            
        elif isinstance ( dataSet , sentence.dataset.DataSet ):
                       
            #get the data in Orange file format
            
            #write the data in a temporary file
            #not secure but we trust our hard disk
            tmpFileName = mktemp(dir='.', suffix='.tab')
            file = codecs.open(tmpFileName, 'w', 'utf-8')
        
            attReader = AttributesReader(file, class_name, meta_attributes, desired_attributes)
            #proceed with parcing
            myparser = make_parser()
            myparser.setContentHandler(attReader)
            myparser.parse(tmpFileName)
            
            sentReader = SentenceReader(file, class_name, meta_attributes, desired_attributes)

#
#            #load the data
#            print "Feeding file to Orange"
#            self.data = orange.ExampleTable(tmpFileName)
#            print "Loaded ", len(self.data) , " sentences from file " , tmpFileName
#            #get rid of the temp file
#            if not keep_temp:
            os.unlink(tmpFileName)
            
        return None
    
    
    def get_data(self):
        return self.data

    
    def get_dataset(self):
        data = self.data
        attribute_names = set() #set containing the attribute names
        new_data = [] #list containing the data, one parallelsentence per entry
        
        
        
        for item in data:
            sentence_attributes = {}
            

            sentence_attributes[item.domain.classVar.name] = str(item.getclass().value)
            
            #first get normal features
            for att in item.domain.attributes:
                sentence_attributes[att.name] = str(item[att].value) 
                attribute_names.add(att.name)

            metas = item.getmetas()
            
            src = SimpleSentence()
            tgt = [SimpleSentence(), SimpleSentence()] #TODO: this will break if more than two SimpleSentences()
            ref = SimpleSentence()
            
            #then get metas
            for key in metas: 
                attribute_name = metas[key].variable.name
                
                if attribute_name == 'src':
                    src = SimpleSentence(metas[key].value)
                elif attribute_name == 'ref':
                    try:
                        ref = SimpleSentence(metas[key].value)
                    except KeyError:
                        pass
                elif (attribute_name.startswith('tgt') and attribute_name.find('_') == -1):
                    tag, index = attribute_name.split( "-")
                    #assume they appear the right order
                    tgt[int(index)-1] = SimpleSentence(metas[key].value)
                    #tgt.append( SimpleSentence ( metas[key].value ) )
                    
                else:
                #if not attribute_names = src|ref|tgt
                    sentence_attributes[attribute_name] = str(metas[key].value) 
                    attribute_names.add(attribute_name)
            
            #create a new sentence and add it to the list
            #print "Creating a sentence"
            #print src
            #print "Target", tgt
            #print ref
            new_parallelsentence = ParallelSentence(src, tgt, ref, sentence_attributes)
            new_parallelsentence.recover_attributes()
            new_data.append(new_parallelsentence)
            
        return DataSet( new_data, attribute_names ) 

    def print_statistics(self): 
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
        


    def __createTempFile__(self):
        tmpFileName = mktemp(dir='.', suffix='.tab')
        file_object = codecs.open(tmpFileName, 'w', 'utf-8')
        return file_object 
    
    def __writeTempFile__(self, data):
        
        tmpFileName = mktemp(dir='.', suffix='.tab')
        file_object = codecs.open(tmpFileName, 'w', 'utf-8')
        file_object.write(data)
        file_object.close()  
        
        return tmpFileName
        
    
    def __get_orange_header__(self, dataset, class_name, attribute_names, desired_attributes=[], meta_attributes=[]):
    
                #first construct the lines for the declaration
        line_1 = "" #line for the name of the arguments
        line_2 = "" #line for the type of the arguments
        line_3 = "" #line for the definition of the class 
        print "Getting attributes"
        
        
        print attribute_names
        if desired_attributes == []:
            desired_attributes = attribute_names
        
        #if no desired attribute define, get all of them
        #if not desired_attributes:
        #    desired_attributes =  attribute_names
        
        print "Constructing file"
        #prepare heading
        for attribute_name in attribute_names :
            #line 1 holds just the names
            line_1 += attribute_name +"\t"
            
            #TODO: find a way to define continuous and discrete arg
            #line 2 holds the class type
            if attribute_name == class_name:
                line_2 += "d\t"
            elif attribute_name in desired_attributes and attribute_name not in meta_attributes:
                #line_2 += "%s\t" % desired_attributes[attribute_name]
                line_2 += "c\t"

            else:
                line_2 += "d\t"

            
            #line 3 defines the class and the metadata
            if attribute_name == class_name:
                line_3 = line_3 + "c"
            elif attribute_name not in desired_attributes or attribute_name in meta_attributes:
                line_3 = line_3 + "m"
            line_3 = line_3 + "\t"
        
        #src
        line_2 += "string\t"
        line_3 += "m\t"
        line_1 += "src\t"
        #target
        i=0
        for tgt in dataset.get_parallelsentences()[0].get_translations():
            i+=1
            line_2 += "string\t"
            line_3 += "m\t"
            line_1 += "tgt-" + str(i) + "\t"
        #ref 
        line_2 += "string\t"
        line_3 += "m\t"
        line_1 += "ref\t"
        
        #break the line in the end
        line_1 = line_1 + "\n"
        line_2 = line_2 + "\n"
        line_3 = line_3 + "\n"
        output = line_1 + line_2 + line_3
        return output
    
    
    def __getOrangeFormat__(self, dataset, class_name, desired_attributes=[], meta_attributes=[]):
        sys.stderr.write("retrieving attribute names\n")
        self.attribute_names = dataset.get_all_feature_names()
        
        sys.stderr.write("processing orange header\n") 
        output = self.__get_orange_header__(dataset, class_name, self.attribute_names, desired_attributes, meta_attributes)
        
        sys.stderr.write("processing content\n")

        outputlines = []

        for psentence in dataset.get_parallelsentences():
            return self.process_parallelsentence(psentence)
        output += "".join(outputlines)
        return output
    
    def process_parallelsentence(self, psentence):
        #sys.stderr.write("getting nested attributes\n")
        nested_attributes = psentence.get_nested_attributes()
        nested_attribute_names = nested_attributes.keys()
        attribute_names = self.attribute_names
        outputlines = []
        
        #sys.stderr.write("printing content\n")
        for attribute_name in attribute_names:
            if attribute_name in nested_attribute_names:
                outputlines.append(nested_attributes[attribute_name])
                
            #even if attribute value exists or not, we have to tab    
            outputlines.append ("\t")
        outputlines.append( psentence.get_source().get_string())
        outputlines.append("\t")
        for tgt in psentence.get_translations():
            outputlines.append(tgt.get_string())
            outputlines.append("\t")
        try:
            outputlines.append(psentence.get_reference().get_string())
            outputlines.append("\t")
        except:
            outputlines.append("\t")
        outputlines.append("\n")
        return outputlines
    
    def split_data(self, percentage):
        size =  len (self.data)
        testSize = round (size * percentage) 
        
        print "Splitting data"
        
        indices = orange.MakeRandomIndices2(p0=testSize)
        indices.stratified = indices.Stratified 
        ind = indices(self.data)
        
        testSet = self.data.select(ind, 0)
        trainingSet = self.data.select(ind, 1)
        
        return [trainingSet, testSet] 
    
     
    
    def cross_validation(self):
        
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
        deepcopy
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
    
    def get_SVM(self):
        l=orange.SVMLearner() 
        l.svm_type=orange.SVMLearner.Nu_SVC 
        l.nu=0.3 
        l.probability=True 
        return l(self.data) 
    
    
    def classify_with(self,classifier):
        """
        Utility function which classifies the test data with the given classifier
        """
        mydata = self.data
        
        for i in range(len(mydata)):
            
        #for ex in mydata:
            try:
                new_value = classifier(mydata[i])
            except:
                print "couldn't apply classifier"
                new_value = "0"
            mydata[i].setclass(new_value)
        return mydata
            
    
    def get_accuracy(self, classifiers):
        correct = [0.0]*len(classifiers)
        wrong = [0.0]*len(classifiers)
        for ex in self.data:
            for i in range(len(classifiers)):
                try:
                    if classifiers[i](ex) == ex.getclass():
                        correct[i] += 1
                    else:
                        wrong[i] += 1
                except:
                    print "kind of error"
                
        for i in range(len(correct)):
            wrong[i] = (correct[i] - wrong[i]) / len(self.data)
            correct[i] = correct[i] / len(self.data)
        return (correct, wrong)
    
        
    
    
    
    
    
    
            

        
        