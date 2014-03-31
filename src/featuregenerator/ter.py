'''
Created on 18 Mar 2014

@author: Eleftherios Avramidis
'''

import tempfile
import os, sys
import subprocess
from featuregenerator import FeatureGenerator
from preprocessor import Tokenizer


SGML_CONTAINER = """<refset trglang="en" setid="12014" srclang="any">
<doc sysid="ref" docid="1" genre="news" origlang="xx">
<seg id="1">{text}</seg>
</doc>
</refset>"""

def wrap_sgml(text):
    tmpfile = tempfile.NamedTemporaryFile(mode='w',delete=False,suffix='.jcml', prefix='tmp_', dir='/tmp')
    content = SGML_CONTAINER.format(text=text)
    tmpfile.write(content)
    tmpfile.close()
    return tmpfile.name

class TerWrapper(FeatureGenerator):
    def __init__(self, ter_path, reverse=True):
        self.path = ter_path
        self.reverse = reverse
        
    def process_item(self, target_text, reference_text):
        hypothesis_filename = wrap_sgml(target_text)
        reference_filename = wrap_sgml(reference_text)
        if self.reverse:
            command = "java -jar {} -r {} -h {}".format(self.path, hypothesis_filename, reference_filename)
        else:
            command = "java -jar {} -h {} -r {}".format(self.path, hypothesis_filename, reference_filename)
        
        #java -jar terSimple.jar -h /home/elav01/taraxu_data/wmt14/1.2/tr.translation.seg -r /home/elav01/taraxu_data/wmt14/1.2/tr.suggestion.seg
        
        #print command
        output = subprocess.check_output(command.split())
        atts = {}
        for line in output.split("\n"):
            if line.startswith("RESULT:"):
                atts = dict([item.split(":") for item in line.split()[1:]])
        atts = dict([("ter_{}".format(item[0]), item[1]) for item in atts.iteritems()])
        #os.unlink(hypothesis_filename)
        #os.unlink(reference_filename)        
        
        return atts
    
    def get_features_tgt(self, simplesentence, parallelsentence):
        try:
            return self.process_item(simplesentence.get_string(), parallelsentence.get_reference().get_string())
        except AttributeError:
            sys.stderr.write("Warning: no reference sentences found")
            return {}
        
if __name__ == '__main__':
    terpath = "/home/elav01/workspace/qualitative/lib/terSimple.jar"
    
    hypothesis_filename = sys.argv[1]
    reference_filename = sys.argv[2]
    scores_filename = sys.argv[3]
    
    
    hypothesis_file = open(hypothesis_filename)
    reference_file = open(reference_filename)
    scores_file = open(scores_filename)
    
    tokenizer = Tokenizer("es") 
    ter = TerWrapper(terpath)
    
    unmatched = 0
    
    i=0
    
#     #test that number of edits is the same on both directions
#     edits = 0
#     shifts = 0
#     for hypothesis in hypothesis_file:
#         hypothesis = hypothesis.strip()
#         reference = reference_file.readline().strip()
#         scores = ter.process_item(hypothesis, reference)
#         invscores = ter.process_item(reference, hypothesis)
#         if scores["edits"] != invscores["edits"]:
#             print "edits",
#             edits +=1
#         if scores["shifts"] != invscores["shifts"]:
#             print "shift",
#             shifts += 1
#         if scores["edits"] != invscores["edits"] or scores["shifts"] != invscores["shifts"]:
#             print
#     print "edits:", edits, "shifts:", shifts
    for hypothesis in hypothesis_file:
        i+=1 
        #hypothesis = tokenizer.process_string(hypothesis.strip()).strip()
        #.replace("-", " - ").replace(" -  - ", " -- ")
        #hypothesis = hypothesis.strip()
        reference = reference_file.readline().strip()

        #hard-coded heuristic replacements for spanish to adapt to score calculation of organizers
        replacements = [("Sra.", "Sra ."),
                        ("Sens .", "Sens."),
                        ("Sen .", "Sen."),
                        ("etc.", "etc ."),
                        ]
        for replacement in replacements:
            reference = reference.replace(replacement[0], replacement[1])
            hypothesis = hypothesis.replace(replacement[0], replacement[1])
        #reference = tokenizer.process_string(reference_file.readline().strip()).strip()#
        #.replace("-", " - ").replace(" -  - ", " -- ")
        #reference = reference_file.readline().strip()
        scores = ter.process_item(hypothesis, reference)
        our_score = float(scores["ter_ter"])
        organizers_score = float(scores_file.readline().strip()) 
        #print organizers_score,our_score, 
        if not (str(organizers_score)==str(our_score)):
            print "False:", i, organizers_score, our_score, scores
            unmatched += 1 
            print "\thyp", hypothesis
            print "\tref", reference
            print
        
    
    print unmatched
    hypothesis_file.close()
    reference_file.close()
    scores_file.close()
    
    #tokenized_hyp = 'En lugar de ello , es algo tan terrible como " un condenado estrangulado en secreto " .'
    #tokenized_ref = 'En lugar de ello , es terriblemente como " un condenado estrangulados en secreto . "'
    #print TerWrapper(terpath).process_item(tokenized_hyp, tokenized_ref)
