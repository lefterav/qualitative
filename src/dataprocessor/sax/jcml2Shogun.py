'''
Created on Sep 17, 2012

@author: jogin
'''
from xml.etree.cElementTree import iterparse
import numpy

'''
First this class extracts values from tgt sentences and saves them into a list.
Second the extracted values are used for SVMlight classifier. 
'''
class Jcml2Shogun():
    def __init__(self, input_xml_filename):
        self.input_filename = input_xml_filename
        self.TAG_SENT = 'judgedsentence'
        self.TAG_SRC = 'src'
        self.TAG_TGT = 'tgt'
        self.TAG_DOC = 'jcml'
        self.attribute_values = []
                
        self.get_jcml_attribute_values()
        
        
    def get_jcml_attribute_values(self):
        source_xml_file = open(self.input_filename, "r")
        # get an iterable
        context = iterparse(source_xml_file, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        print root
        
        for event, elem in context:
            # create new list
            if event == "start" and elem.tag == self.TAG_SENT:
                self.attribute_values.append([])
            # get tgt values into a list
            elif event == "start" and elem.tag == self.TAG_TGT:
                values = elem.attrib.values()
                self.attribute_values[-1].append(values)
                self.remove_not_numbers() # remove infinities and strings
        
        #for snt in self.attribute_values:
        #    print snt


    # remove infinities and strings
    def remove_not_numbers(self):
        self.attribute_values[-1][-1].pop(24) # inf
        self.attribute_values[-1][-1].pop(23) # inf
        self.attribute_values[-1][-1].pop(22) # inf
        self.attribute_values[-1][-1].pop(19) # inf
        self.attribute_values[-1][-1].pop(11) # string
        self.attribute_values[-1][-1].pop(9) # inf
        self.attribute_values[-1][-1].pop(8) # inf
        self.attribute_values[-1][-1].pop(6) # string
        self.attribute_values[-1][-1].pop(1) # inf


    '''
    TODO (Python 2.7, shogun corresponding libraries, ...)
    '''
    def classifier_svmlight_linear_term_modular(self, fm_train_dna=traindna,fm_test_dna=testdna, \
                                                    label_train_dna=label_traindna,degree=3, \
                                                    C=10,epsilon=1e-5,num_threads=1):
        
        from shogun.Features import StringCharFeatures, DNA, BinaryLabels
        from shogun.Kernel import WeightedDegreeStringKernel
        from shogun.Classifier import SVMLight
        
        feats_train=StringCharFeatures(DNA)
        feats_train.set_features(fm_train_dna)
        feats_test=StringCharFeatures(DNA)
        feats_test.set_features(fm_test_dna)
        
        kernel=WeightedDegreeStringKernel(feats_train, feats_train, degree)
        
        labels=BinaryLabels(label_train_dna)
        
        svm=SVMLight(C, kernel, labels)
        svm.set_qpsize(3)
        svm.set_linear_term(-numpy.array([1,2,3,4,5,6,7,8,7,6], dtype=numpy.double));
        svm.set_epsilon(epsilon)
        svm.parallel.set_num_threads(num_threads)
        svm.train()
        
        kernel.init(feats_train, feats_test)
        out = svm.apply().get_labels()
        return out,kernel

Jcml2Shogun('wmt08.if.partial.jcml')