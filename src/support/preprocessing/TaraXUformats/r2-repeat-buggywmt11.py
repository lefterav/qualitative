'''
Created on 24 Apr 2012

@author: elav01
'''

from xml.etree.ElementTree import ElementTree
from xml.sax.saxutils import unescape
import sys
import re

if __name__ == '__main__':
    
    #pattern = re.compile("(&[^&]{1,4};)")
    tree = ElementTree()
    tree.parse(sys.argv[1])
    
    segments_clean = set()
    
    for treeset in tree.iter("set"):
        for seg in treeset.iter("seg"):
            
            isbuggy = False
            
            for translation in seg.iter("translation"):
                #fixed_translation, changes = pattern.subn(lambda m: unescape(m.group(0)), translation.text)
                fixed_translation = translation.text.replace("&quot;",'"')
                fixed_translation = fixed_translation.replace("&#39;", "'")
    

                if fixed_translation != translation.text:
                    isbuggy = True
            
            if not isbuggy:
                segments_clean.add(seg)
                
        
        for seg in segments_clean:     
            treeset.remove(seg)
        
    tree.write(sys.argv[2])
            
            
            
            
        
