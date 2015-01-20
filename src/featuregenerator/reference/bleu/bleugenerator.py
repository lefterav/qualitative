'''
Contains feature generator for adding BLEU score as an attribute
Created on 07.10.2011

@author: Eleftherios Avramidis
'''

from featuregenerator.featuregenerator import FeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer 
from tempfile import mktemp

from os import unlink 
import os
import subprocess
import sys
import codecs
import bleu


  

class BleuGenerator(FeatureGenerator):
    '''
    Provides BLEU score against the reference
    '''
    
    def get_features_tgt(self, target, parallelsentence):
        """
        Calculates BLEU score for the given target sentence, against the reference sentence
        @param simplesentence: The target sentence to be scored
        @type simplesentence: sentence.sentence.SimpleSentence
        @rtype: dict
        @return: dictionary containing Levenshtein distance as an attribute 
        """
        target_untokenized = target.get_string()
        try:
            ref_untokenized = parallelsentence.get_reference().get_string()

            bleu_value = bleu.score_sentence(target_untokenized, [ref_untokenized])
            return {'ref-bleu': '{:.4}'.format(bleu_value)}
        except:
            return {}



class CrossBleuGenerator(FeatureGenerator):
    '''
    Provides cross-BLEU score of the current target sentence against the others
    '''
    
    def get_features_tgt(self, translation, parallelsentence):
        current_system_name = translation.get_attribute("system")
        alltranslations = dict([(t.get_attribute("system"), t.get_string()) for t in parallelsentence.get_translations()])
        del(alltranslations[current_system_name])
        references = alltranslations.values()
        bleu_value = bleu.score_sentence(translation.get_string(), references)
        return {'cross-bleu': '{:.4}'.format(bleu_value)}
        
            
            
        
        
        
        
    


#    def bleu(self, translation, reference):
#        
#        translation = " ".join(PunktWordTokenizer().tokenize(translation))
#        tfilename = mktemp(dir=u'/tmp/', suffix=u'.tgt.txt')
#        tfile = codecs.open(tfilename, 'w', 'utf-8')
#        tfile.write(translation)
#        tfile.close()
#        
#        reference = " ".join(PunktWordTokenizer().tokenize(reference))
#        rfilename = mktemp(dir=u'/tmp/', suffix=u'.ref.txt')
#        rfile = codecs.open(rfilename, 'w', 'utf-8')
#        rfile.write(reference)
#        rfile.close()
#        
#        ofilename = mktemp(dir=u'/tmp/', suffix=u'.out.txt')
#        ofile = codecs.open(ofilename, 'w', 'utf-8')
#        
#        path = os.path.dirname(__file__)
#        bleupath = os.path.join(path, "bleu")
#        print bleupath
#        subprocess.call([bleupath, "-s" , "-p", "-S", "-r", rfilename, tfilename], stdout = ofile)
#        ofile.close()
#        ofile = codecs.open(ofilename, 'r', 'utf-8')
#        output = ofile.readline()
#        output = float(output)
#        return output
#
#        
        


    
        
