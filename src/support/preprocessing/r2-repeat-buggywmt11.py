'''
Created on 24 Apr 2012

@author: elav01
'''

from xml import etree
import sys

if __name__ == '__main__':
    
    pattern = re.compile("&amp;\([^\&]\{1,4\};\)")
    tree = ElementTree()
    tree.parse(sys.argv[1])
    
    segments_clean = set()
    
    for seg in tree.iter("seg"):
        
        for translation in seg.iter("translation"):
            fixed_translation, changes = pattern.subn("\1", translation.text)
            if changes == 0:
                segments_clean.add(seg)
    
    for seg in segments_clean:
        tree.remove(seg)
    
    tree.write(sys.argv[2])
            
            
            
            
        