"""
@author: Eleftherios Avramidis

Wraps a simple text file (sentence per line) into plain SGML
"""

import getopt
import codecs
import sys


class _Input:
    setname = "set"
    lang = "any"
    docid = "testdoc"
    genre = "news" 
    origlang = "en"
    settype = "srcset"
    sysid = "ref"
    pass
    
    

# Function prints a list of all required and possible parameters.
def help():
    print "\nList of parameters:"
    print "--setname [Source set name]"
    print "--lang [Content language or 'any']"
    print "--docid [String relevant to the document ID]"
    print "--genre [Genre of the content]"
    print "--origlang [Original (not actual) language of the content or 'any']"
    print "--settype [refset|srcset|tstset]"
    print "--sysid [String relevant to the system ID or 'ref']"   


# Function checks, if the user gave all required arguments.
def check_args(Input):
    stop = False
    if stop:
        sys.exit("Program terminated.")


# Function reads the command line arguments, saves them to the Input class
# variables and checks, if the user gave all required arguments.
def read_commandline_args(Input):
    try:
        args = getopt.getopt(sys.argv[1:], "" , ["setname=", "lang=", "docid=" , "genre=", "origlang=", "settype=", "sysid="])[0]
    except getopt.GetoptError:
        help()
        sys.exit("Program terminated.")
        
    for opt, arg in args:
        if opt == '--setname': Input.setname = arg
        if opt == '--lang': Input.lang = arg
        if opt == '--docid': Input.docid = (arg)
        if opt == '--genre': Input.genre = (arg)
        if opt == '--origlang': Input.origlang = arg
        if opt == '--settype': Input.settype = (arg)
        if opt == '--sysid': Input.sysid = (arg)
            
    check_args(Input)
    
    return Input




if __name__ == '__main__':
    
    #be unicode compatible
    sys.stdout = codecs.getreader('utf-8')(sys.stdout)
    sys.stdin = codecs.getwriter('utf-8')(sys.stdin)
    
    
    Input = _Input()
    # Reads the command line input arguments. Explains what is the correct syntax
    # in case of wrong input arguments and stops the program run.
    Input = read_commandline_args(Input)
    
    
    sysidtag = ""
    langtag = ""
    if Input.settype == "srcset":
        langtag = 'srclang="%s"' % Input.lang
    elif Input.settype == "refset" or Input.settype == "tstset":
        langtag = 'trglang="%s" srclang="%s"' % (Input.lang, Input.origlang)
        sysidtag = ' sysid="ref"'

    print '<%s setid="%s" %s>' % (Input.settype, Input.setname, langtag)
    print '<doc%s docid="%s" genre="%s" origlang="%s">' % (sysidtag, Input.docid, Input.genre, Input.origlang)
    i=0
    for line in sys.stdin :
       i+=1
       line = line.replace("\n"," ")
       print '<seg id="'+str(i)+'">' + line.strip() +'</seg>'
    
    print '</doc>'
    print '</%s>' % Input.settype
        
        
    
    
