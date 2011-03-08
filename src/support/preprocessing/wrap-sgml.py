'''
@author: Eleftherios Avramidis
'''


"""
Wraps a simple text file (sentence per line) into plain SGML
"""


import codecs
import sys

if __name__ == '__main__':
    
    sys.stdout = codecs.getreader('utf-8')(sys.stdout)
    sys.stdin = codecs.getwriter('utf-8')(sys.stdin)
    name = "multiUN"

    print '<srcset setid="' + name + '" srclang="any">'
    print '<doc docid="testset" genre="news" origlang="any">'
    i=0
    for line in sys.stdin :
       i+=1
       line = line.replace("\n"," ")
       print '<seg id="'+str(i)+'">' + line +'</seg>'
    
    print '</doc>'
    print '</srcset>'
        
        
    
    