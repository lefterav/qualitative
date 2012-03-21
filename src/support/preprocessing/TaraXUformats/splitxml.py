'''
Created on 16 Mar 2012

@author: elav01
'''


try:
  from lxml import etree
  #print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    #print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      #print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        #print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          #print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree library from any known place")


from copy import deepcopy
import sys

if __name__ == '__main__':
    
    
    #f1 = open('/home/elav01/taraxu_data/r2/r2-output/aaa.xml', 'r')
    #f2 = open('/home/elav01/taraxu_data/r2/r2-output/aaa2.xml', 'w')
    
        
    try:
        f = open(sys.argv[1])
        first_sentence = int(sys.argv[2])
        last_sentence = int(sys.argv[3])+1
    
    except:    
        print "Please provide an XML file and the index of the first and last sentence you want to keep"
        print "Indexes start at 1"
        print
        print "{0} <file.xml> first_sentence last_sentence"
        sys.exit(1)
    
    tree = etree.parse(f)
    root = tree.getroot()
    children = root.getchildren()
    
    i = 0
    for child in children:
        i+=1
        if i not in range(first_sentence, last_sentence) :
            root.remove(child)
            
    print '<?xml version="1.0" encoding="UTF-8"?>'
    print etree.tostring(root, pretty_print=True) 
    
    
