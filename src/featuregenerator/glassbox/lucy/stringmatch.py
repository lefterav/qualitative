'''
Get the original text, and a text where sentences have been segmented
by Lucy and gather trees per original text sentence

Created on Dec 24, 2013

@author: Eleftherios Avramidis
'''

from xml.etree.cElementTree import iterparse
import sys

TAG_SRC = "source"
TAG_TREE = ["analysisTree", "transferTree", "generationTree"]


#        desired_source = []

def match(txtsentence, treesentence, threshold=4):
    txtsentence = txtsentence.split()
    treesentence = treesentence.split()
    if threshold>len(txtsentence) and threshold>len(treesentence):
        threshold = max([len(txtsentence),len(treesentence)])
    for i in range(0, threshold):
        try:
            txt_i = txtsentence[i]
            tree_i = treesentence[i]
            if not txt_i == tree_i:
                return False
        except IndexError:
            return False
    return True
            
            
if __name__ == '__main__':
    input_xml_filename = sys.argv[1]
    input_text_filename = sys.argv[2]
    
    parallelsentences = []
    source_xml_file = open(input_xml_filename, "r")
    source_textfile = open(input_text_filename, 'r')
    
    # get an iterable
    context = iterparse(source_xml_file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()
    
    attributes = []
    target_id = 0

    
    
    nexttxtsentence = source_textfile.readline()
    document_trees = []
    treesentence = []
    sentence_trees = []
    
    for event, elem in context:
        current_tree = {}
        #new sentence: get attributes
        
        if event == "start" and elem.tag == TAG_SRC:
            treesentence = elem.text
            #get a new line from the text file
            print ">?" , treesentence
            if (not treesentence) or match(nexttxtsentence, treesentence): 
                nexttxtsentence = source_textfile.readline()
                print nexttxtsentence
                document_trees.append(sentence_trees)
                sentence_trees = []
                
        if event == "end" and elem.tag in TAG_TREE:
            #one dict to hold analysis, transfer and generation tree 
            #for the same sentence
            current_tree[elem.tag] = elem.text
            sentence_trees.append(current_tree)
                            
        root.clear()
        
    
    
