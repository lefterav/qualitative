"""
@author: Eleftherios Avramidis
"""

from xml.dom import minidom
from sentence.parallelsentence import ParallelSentence
from xml.sax.saxutils import escape
from sentence.dataset import DataSet


class GenericWriter(object):
    def __init__(self, data):
        raise NotImplementedError( "Should have implemented this" )
    
    def write_to_file(self, filename):
        raise NotImplementedError( "Should have implemented this" ) 
    
    def get_parallelsentence_string(self, ps):
        raise NotImplementedError( "Should have implemented this" ) 
    

class GenericXMLWriter(GenericWriter):
    def __init__(self, data = None):
        """
        Constructor
        """
        if isinstance (data, minidom.Document):
            self.object_xml = data
        elif isinstance(data, list):
            self.object_xml = self.get_document_xml(data)
        elif isinstance(data, DataSet):
            self.object_xml = self.get_document_xml(data.get_parallelsentences())
        else:
            pass
    
    def get_parallelsentence_xml(self, ps):
        raise NotImplementedError( "Should have implemented this" ) 
      
    
    def get_parallelsentence_string(self, ps):
        return self.get_parallelsentence_xml(ps).toprettyxml("\t","\n", "utf-8")
    
    def get_document_xml(self, parallelsentences):
        """
        Creates an XML for the document an populates that with the (parallel) sentences of the given object.
        Resulting XML object gets stored as a variable.
        @param parallelsentences: a list of ParallelSentence objects 
        """
        doc_xml = minidom.Document( )
        jcml = doc_xml.createElement("jcml")
        
        i=0
        
        
        for ps in parallelsentences:
            parallelsentence_xml = self.get_parallelsentence_xml(ps, doc_xml)
            jcml.appendChild(parallelsentence_xml)
            
            #print ">", i
            i += 1
        
        doc_xml.appendChild(jcml)
        return doc_xml
    
    
    def write_to_file(self, filename):
        file_object = open(filename, 'w')
        try:
            file_object.write(self.object_xml.toprettyxml("\t","\n")) #removed ,"utf-8"
        except:
            file_object.write(self.object_xml.toprettyxml("\t","\n", "utf-8"))            
        file_object.close()  
        
    


class XmlWriter(GenericXMLWriter):
    """
    classdocs
    """


    
                
    
    

    def get_parallelsentence_xml(self, ps, doc_xml = minidom.Document()):
        parallelsentence_xml = doc_xml.createElement("judgedsentence")
        
        #add attributes of parallel sentence
        for attribute_key in ps.get_attributes().keys():
            parallelsentence_xml.setAttribute(attribute_key.decode('utf-8') , ps.get_attribute(attribute_key).decode('utf-8'))
        
        #add source as a child of parallel sentence
        src_xml = self.__create_xml_sentence__(doc_xml, ps.get_source(), "src")
        parallelsentence_xml.appendChild(src_xml)

        #add translations
        for tgt in ps.get_translations():
            tgt_xml = self.__create_xml_sentence__(doc_xml, tgt, "tgt")
            parallelsentence_xml.appendChild(tgt_xml)

        #add reference as a child of parallel sentence
        if ps.get_reference():
            ref_xml = self.__create_xml_sentence__(doc_xml, ps.get_reference(), "ref")
            parallelsentence_xml.appendChild(ref_xml)

            #append the newly populated parallel sentence to the document
        return parallelsentence_xml
            

        
        

           
        
        
    def __create_xml_sentence__(self, doc_xml, sentence, tag):
        """
        Helper function that fetches the text and the attributes of a sentence
        and wraps them up into a minidom XML sentenceect
        """
        
        sentence_xml = doc_xml.createElement(tag)

        for attribute_key in sentence.get_attributes().keys():
            try:
                sentence_xml.setAttribute(attribute_key.decode('utf-8'), escape(str(sentence.get_attribute(attribute_key).decode('utf-8'))))
            except:    
                sentence_xml.setAttribute(attribute_key, escape(str(sentence.get_attribute(attribute_key))))
        textnode = escape(sentence.get_string().strip()).decode('utf-8')     
        sentence_xml.appendChild(doc_xml.createTextNode(textnode))
        
        return sentence_xml
        