'''
Created on 9 Nov 2012

@author: elav01
'''

import sys

if __name__ == '__main__':
    file1 = open(sys.argv[1], 'r')
    file2 = open(sys.argv[2], 'r')
    
    matched = []
    threshold = 0.4
    highmatched = []
    k = 0
#    print  "Length of file" ,len(file1.readlines())
    for line1 in file1:
        i=0
        file2.seek(0)
        line1 = line1.lower().strip()
        set1 = set(line1.split()) 
        for line2 in file2:
            line2 = line2.lower().strip()
#            print k, i  
            set2 = set(line2.split())
            intersection = set2.intersection(set1)
            matched.append(len(intersection))
            #if 1.00*len(intersection)/len(set2) > threshold:
            #    highmatched.append((k, i, 1.00*len(intersection)/len(set2), line1, line2 ))
            if line1 == line2:
            
                highmatched.append((k, i, 1.00*len(intersection)/len(set2), line1, line2 ))
            i+=1
        k+=1
  

    file1.close()
    file2.close()
    for h in highmatched:
        h = [str(j) for j in h]
        print "\t".join(h)
    print 1.00*sum(matched)/len(matched)
