'''
Created on 23 Feb 2012

@author: lefterav
'''
from optparse import OptionParser
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from io.sax.saxps2jcml import Parallelsentence2Jcml

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-s", "--source", dest="source_filename",
                      help="read one source sentence per line from FILE", metavar="FILE")
    parser.add_option("-t", "--translation", dest="target_filename",
                      help="read one translation output sentence per line from FILE", metavar="FILE")
  
    parser.add_option("-r", "--reference", dest="reference_filename",
                      help="read one reference sentence per line from FILE", metavar="FILE")
    
    parser.add_option("-l", "--score", dest="score_filename",
                      help="read one score per line from FILE", metavar="FILE")
    
    parser.add_option("-o", "--output", dest="output_filename",
                      help="write output to this jcml FILE", metavar="FILE")
    
    (opt, args) = parser.parse_args()
    
    source_file = open(opt.source_filename, 'r')
    target_file = open(opt.target_filename, 'r')
    reference_file = open(opt.reference_filename, 'r')
    score_file = open(opt.score_filename)
    
    parallelsentences = []
    
    for source_line in source_file:
        source_line = source_line.strip()
        target_line = target_file.readline().strip()
        reference_line = reference_file.readline().strip()
        score = score_file.readline().strip()
        
        source_sentence = SimpleSentence(source_line)
        target_sentences = [SimpleSentence(target_line, {"rank": score})]
        reference_sentence = SimpleSentence(reference_line)
        
        
        ps = ParallelSentence(source_sentence, target_sentences, reference_sentence)
        parallelsentences.append(ps)
    
    Parallelsentence2Jcml(parallelsentences).write_to_file(opt.output_filename)
    
