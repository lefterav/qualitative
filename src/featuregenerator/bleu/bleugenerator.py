'''
Created on 07.10.2011

@author: elav01
'''

from featuregenerator.featuregenerator import FeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer 
from tempfile import mktemp

from os import unlink 
import subprocess
import sys
import codecs

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
        
        translation = " ".join(PunktWordTokenizer().tokenize(translation))
        tfilename = mktemp(dir=u'/tmp/', suffix=u'.tgt.txt')
        tfile = codecs.open(tfilename, 'w', 'utf-8')
        tfile.write(translation)
        tfile.close()
        
        reference = " ".join(PunktWordTokenizer().tokenize(reference))
        rfilename = mktemp(dir=u'/tmp/', suffix=u'.ref.txt')
        rfile = codecs.open(rfilename, 'w', 'utf-8')
        rfile.write(reference)
        rfile.close()
        
        ofilename = mktemp(dir=u'/tmp/', suffix=u'.out.txt')
        ofile = codecs.open(ofilename, 'w', 'utf-8')
        
        path = [path for path in sys.path if path.endswith("src")][0]
        bleupath = "%s/featuregenerator/bleu/bleu" % path
        subprocess.call([bleupath, "-s" , "-p", "-S", "-r", rfilename, tfilename], stdout = ofile)
        ofile.close()
        ofile = codecs.open(ofilename, 'r', 'utf-8')
        output = ofile.readline()
        output = float(output)
        return output

        
        
        

    
        
