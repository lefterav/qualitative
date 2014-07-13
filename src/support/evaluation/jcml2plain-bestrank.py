'''
Created on 19 Oct 2011

@author: Eleftherios Avramidis
'''
import sys
import codecs

if __name__ == '__main__':
    from io_utils.input.jcmlreader import JcmlReader
    #filename_in = "/home/Eleftherios Avramidis/taraxu_data/ml4hmt/5/classified.jcml"
    #filename_out = "/home/Eleftherios Avramidis/taraxu_data/ml4hmt/5/bestselected.txt"
    #rank_attribute = "orig_rank"
    filename_in = sys.argv[1]
    filename_out = sys.argv[2]
    rank_attribute = sys.argv[3]
    
    file_out = codecs.open(filename_out, 'w', 'utf-8')

    parallelsentences = JcmlReader(filename_in).get_parallelsentences()
    for parallelsentence in parallelsentences:
        for tgt in parallelsentence.get_translations():
            rank = int(tgt.get_attribute(rank_attribute))
            if rank == 1:
                file_out.write(tgt.get_string() + "\n")
                break
    file_out.close()