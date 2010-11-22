'''
@author: Eleftherios Avramidis
'''

from xml.dom import minidom


class XmlWriter(object):
    '''
    classdocs
    '''


    def __init__(self, parallelsentences):
        '''
        Constructor
        '''
        xml_doc = minidom.Document( )
        xml_doc.createElement("jcml")
        
        for parallelsentence in parallelsentences:
            xml_psentence = minidom.Node()
            
        
        
        
        
        