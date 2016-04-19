'''
Created on 26 Nov 2014

@author: Eleftherios Avramidis
'''

from sentence.sentence import SimpleSentence

class Worker:
    """
    Abstract class for translation engine workers
    """
    def translate(self, string):
        """
        Translate given string and return the result and any translation information
        @param string: the string to be translated
        @type string: string
        @return translated_string, translation_info
        @rtype: string, dict of (string, float) or (string, int) or (string, string)
        """
        raise NotImplementedError("This function needs to be implemented by a subclass of Worker")

        
        
        