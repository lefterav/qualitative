from dataprocessor.sax.utils import filter_jcml
import sys
import logging as log

def filter_targetsentence(parallelsentence, **kwargs):
    ids = [int(i) for i in kwargs["ids"]]
    return (int(parallelsentence.get_attribute("id"))-1 not in ids)
    
if __name__ == '__main__':    
    #logging
    log.basicConfig(level=log.INFO)

    ids = [line.split()[0] for line in open(sys.argv[1])]
    filter_jcml(sys.argv[2], sys.argv[3], filter_targetsentence, ids=ids)
    

