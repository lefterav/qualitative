'''
Created on 07.10.2011

@author: elav01
'''

from featuregenerator.featuregenerator import FeatureGenerator
#from nltk.tokenize.punkt import PunktWordTokenizer 
from tempfile import mktemp

from os import unlink 
import subprocess

class BleuGenerator(FeatureGenerator):
    '''
    classdocs
    '''
    
    def get_features_tgt(self, target, parallelsentence):
        """
        Calculates Levenshtein distance for the given target sentence, against the reference sentence
        @param simplesentence: The target sentence to be scored
        @type simplesentence: sentence.sentence.SimpleSentence
        @rtype: dict
        @return: dictionary containing Levenshtein distance as an attribute 
        """
        target_untokenized = target.get_string()
        ref_untokenized = parallelsentence.get_reference().get_string()

        bleu_value = self.bleu(target_untokenized, ref_untokenized)
        return {'bleu': str(bleu_value)}


    def bleu(self, translation, reference):
        
        #translation = " ".join(PunktWordTokenizer().tokenize(translation))
        tfilename = mktemp(dir=u'/tmp/', suffix=u'.tgt.txt')
        tfile = open(tfilename, 'w')
        tfile.write(translation)
        tfile.close()
        
        #reference = " ".join(PunktWordTokenizer().tokenize(reference))
        rfilename = mktemp(dir=u'/tmp/', suffix=u'.ref.txt')
        rfile = open(rfilename, 'w')
        rfile.write(reference)
        rfile.close()
        
        ofilename = mktemp(dir=u'/tmp/', suffix=u'.out.txt')
        ofile = open(ofilename, 'w')
        
        
        subprocess.call(["./bleu", "-r", rfilename, "-s" , "-S", tfilename], stdout = ofile)
        
        ofile.close()
        ofile = open(ofilename, 'r')
        output = float(ofile.readline())
        
        return output
    

        
        
        

    
        