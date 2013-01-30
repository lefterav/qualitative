'''
Created on Jan 22, 2013

@author: dupo
'''

from xml.etree.cElementTree import iterparse
from numpy import *
from optparse import OptionParser
import sys
import os
import shutil

class JoinPlainTextFeatures:
    
    def _get_feature_names(self, feature_description_filename):
        feature_description_file = open(feature_description_filename, 'r')
        context = iterparse(feature_description_file, events=("start", "end"))
        context = iter(context)
        event, root = context.next()
        feature_names = []
        for event, elem in context:                
            if event == "end" and elem.tag == self.TAG_SRC:
                feature_names.append(elem.attrib['index'])
            root.clear()
        return feature_names
    
    def add_features(self, existing_jcml, max_targets, feature_description_filename):
        jcml_file = open(existing_jcml, "r")
        features_dir = existing_jcml.replace("jcml", "plain")
        updated_jcml = existing_jcml.replace("jcml", "updated.jcml")
        feature_names = self._get_feature_names(feature_description_filename)
#        source_filename = os.path.join(newdir, "source")
#        source_file = open(source_filename, 'r')        
        #empty list containing the file objects to write to
        target_files = []
        
        for i in xrange(1,max_targets+1):
            newsubdir = os.path.join(newdir, str(i))
            results_filename = os.path.join(newsubdir, resultsfilename)
            results_file = open(results_filename, 'r')
            results_files.append(results_file)
            
        target_texts = []
        
        # get an iterable
        context = iterparse(jcml_file, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        #iterate over the XML tree
        
        target_id = 0
        
        for event, elem in context:                
            if event == "end" and elem.tag == self.TAG_SRC:
                pass
            elif event == "end" and elem.tag == self.TAG_TGT:
                results_line = results_file[target_id].readline()
                feature_values = results_line.split('\t')
                feature_tuples = zip(feature_names, feature_values)
                feature_dic = dict(feature_tuples)
                elem.attrib.update(feature_dic)
                target_id += 1
                                
            elif event == "end" and elem.tag == self.TAG_SENT:
                target_id = 0                
                
        #close open file objects
#        source_file.close()
        for i, target_file in enumerate(target_files, 1):
            newsubdir = os.path.join(newdir, str(i))
            shutil.copy(source_filename, os.path.join(newsubdir, os.path.basename(source_filename)))
            target_file.close()
            
        jcml_file.close()
        
        output_jcml_file = open()

class Jcml2PlainText:
    
    def __init__(self, sourcelang, targetlang):
        self.TAG_DOC = 'jcml'
        self.TAG_SENT = 'judgedsentence'
        self.TAG_SRC = 'src'
        self.TAG_TGT = 'tgt'
        self.TAG_REF = 'ref'
        

    def convert(self, jcml_filename, max_targets=12):
        jcml_file = open(jcml_filename, "r")        
        newdir = jcml_filename.replace("jcml", "plain")
        try:
            os.makedirs(newdir)
        except:
            pass
        
        source_filename = os.path.join(newdir, "source")
        source_file = open(source_filename, 'w')        
        #empty list containing the file objects to write to
        target_files = []
        
        for i in xrange(1,max_targets+1):
            newsubdir = os.path.join(newdir, str(i))
            try:
                os.makedirs(newsubdir)
            except:
                pass
            target_filename = os.path.join(newsubdir, "target")
            target_file = open(target_filename, 'w')
            target_files.append(target_file)
        
        
        target_texts = []
        
        # get an iterable
        context = iterparse(jcml_file, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        #iterate over the XML tree
        for event, elem in context:                
            if event == "end" and elem.tag == self.TAG_SRC:
                source_file.write(elem.text)
                source_file.write("\n")
            
            elif event == "end" and elem.tag == self.TAG_TGT:
                target_texts.append(elem.text)
                
            elif event == "end" and elem.tag == self.TAG_SENT:
                for target_file in target_files:
                    try:
                        text = target_texts.pop(0)
                    except:
                        text = "@@=)>"
                    target_file.write(text)
                    target_file.write("\n")                            
                target_texts = []
                
                
            root.clear()       
                
        #close open file objects
        source_file.close()
        for i, target_file in enumerate(target_files, 1):
            newsubdir = os.path.join(newdir, str(i))
            shutil.copy(source_filename, os.path.join(newsubdir, os.path.basename(source_filename)))
            target_file.close()
                    
#if __name__ == '__main__':
#    convertor = Jcml2PlainText(sys.argv[3], sys.argv[4])
#    convertor.convert(sys.argv[1], int(sys.argv[2]))

if __name__ == '__main__':
    convertor = JoinPlainTextFeatures()
    existing_jcml = sys.argv[1]
    max_targets = sys.argv[3]
    feature_description_filename = sys.argv[4]
    convertor.add_features(existing_jcml, max_targets, feature_description_filename)

