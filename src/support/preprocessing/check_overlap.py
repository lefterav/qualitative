'''
Created on 9 Nov 2012

@author: elav01
'''

import sys

if __name__ == '__main__':
    file1_src = open(sys.argv[1], 'r')
    file1_tgt = open(sys.argv[2], 'r')
    file2 = open(sys.argv[3], 'r')
    
    try:
       filtering = (sys.argv[4] == '--filter')
       filteredfile_src = open(sys.argv[5], 'w')
       filteredfile_tgt = open(sys.argv[6], 'w')
    except:
       filtering = False 

    matched = []
    threshold = 0.4
    highmatched = []
    k = 0
#    print  "Length of file" ,len(file1.readlines())
    highmatchedlines = []
    nonmatchedlines = []
    for line1, line1_tgt in zip(file1_src, file1_tgt):
        i=0
        file2.seek(0)
        line1 = line1.lower().strip()
        set1 = set(line1.split()) 
        approvedline = True
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
                highmatchedlines.append(k)
                approvedline = False
            i+=1

        if approvedline: 
            filteredfile_src.write("{}\n".format(line1))
            filteredfile_tgt.write("{}\n".format(line1_tgt))
                
        k+=1
  

    file1_src.close()
    file1_tgt.close()
    file2.close()

            
    
    filteredfile_src.close()
    filteredfile_tgt.close()


 
    for h in highmatched:
        h = [str(j) for j in h]
        print "\t".join(h)
    print 1.00*sum(matched)/len(matched)
