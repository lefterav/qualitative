'''
Created on 23 Feb 2012

@author: lefterav
'''
from optparse import OptionParser
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-s", "--source", dest="source_filename",
                      help="read one source sentence per line from FILE", metavar="FILE")
    
    parser.add_option("-t", "--translation", dest="target_filename",
                      help="read one translation output sentence per line from FILE", metavar="FILE")
    
    parser.add_option("-m", "--system", dest="system_name",
                      help="system name")
    
  
    parser.add_option("-r", "--reference", dest="reference_filename",
                      help="read one reference sentence per line from FILE", metavar="FILE")
    
    parser.add_option("-l", "--score", dest="score_filename",
                      help="read one score per line from FILE", metavar="FILE")
    
    parser.add_option("-a", "--feature-names", dest="feature_names", action="append", type="str",
                      help="a list of feature names")
    
    parser.add_option("-q", "--feature-files", dest="feature_files", action="append", type="str",
                      help="a list of feature FILEs in respective order", metavar="FILE")
    
    parser.add_option("-o", "--output", dest="output_filename",
                      help="write output to this jcml FILE", metavar="FILE")
    
    parser.add_option("-f", "--langsrc", dest="langsrc",
                      help="source language code")
    
    parser.add_option("-e", "--langtgt", dest="langtgt",
                      help="target language code")
    
    parser.add_option("-u", "--testset", dest="testset",
                      help="set name")
    
    
    (opt, args) = parser.parse_args()
    
    source_file = open(opt.source_filename, 'r')
    target_file = open(opt.target_filename, 'r')
    try:
        reference_file = open(opt.reference_filename, 'r')
    except:
        reference_file = None
    try:
        score_file = open(opt.score_filename)
    except:
        score_file = None
    

    
    parallelsentences = []
    i = 0
    
    for source_line in source_file:
        i+=1
        atts = {}
        source_line = source_line.strip()
        target_line = target_file.readline().strip()
        if reference_file:
            reference_line = reference_file.readline().strip()
            reference_sentence = SimpleSentence(reference_line)
        else:
            reference_sentence = None
        
        if score_file:
            score = score_file.readline().strip()
            atts["score"] = score
        
        atts["system"] = opt.system_name
        
        source_sentence = SimpleSentence(source_line)
        target_sentences = [SimpleSentence(target_line, atts)]
        
        ps_atts =  {"langsrc" : opt.langsrc ,
                     "langtgt" : opt.langtgt ,
                     "testset" : opt.testset ,
                     "id" : str(i)}
        
        ps = ParallelSentence(source_sentence, target_sentences, reference_sentence, ps_atts)
        parallelsentences.append(ps)
    
    Parallelsentence2Jcml(parallelsentences).write_to_file(opt.output_filename)
    
