'''
Created on 26 Nov 2014

@author: Eleftherios Avramidis
'''

from sentence.sentence import SimpleSentence

class Worker(object):
    """
    Abstract class for translation engine workers
    """
    def translate(self, string, **kwargs):
        """
        Translate given string and return the result and any translation information
        @param string: the string to be translated
        @type string: string
        @return translated_string, translation_info
        @rtype: tuple of string and a dict of (string, float) or (string, int) or (string, string)
        """
        raise NotImplementedError("This function needs to be implemented by a subclass of Worker")
    
    
    def translate_batch(self, strings):
        """
        Translate many strings and return a list of results and any translation information
        Should be overriden by workers, if translating an entire batch is more efficient than sending
        a separate request per string
        @param strings: the strings to be translated
        @type strings: list of string
        @return translated_strings, translation_info
        @rtype: list of tuples of string and a dict of (string, float) or (string, int) or (string, string)
        """
        for string in strings:
            yield self.translate(string)

        
        
        