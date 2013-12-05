'''
Remove from a parallel document sentences that are found in a test set

Created on 9 Nov 2012

@author: Eleftherios Avramidis
'''

import sys

'''
parameters:
source-language side of parallel set
target-language side of parallel set
source-language side of test set
preferred name of source language side of parallel set after test sentences removed
preferred name of target language side of parallel set after test sentences removed

'''



if __name__ == '__main__':
    #open files    
    file1_src = open(sys.argv[1], 'r')
    file1_tgt = open(sys.argv[2], 'r')
    file2 = open(sys.argv[3], 'r')
    
    #these parameters should be always given
    try:
       filtering = (sys.argv[4] == '--filter')
       filteredfile_src = open(sys.argv[5], 'w')
       filteredfile_tgt = open(sys.argv[6], 'w')
    except:
       filtering = False 

    len_file2 = len(file2.readlines())
    file2.close()
    file2 = open(sys.argv[3], 'r')

    #basic settings
    matched = []
    threshold = 0.8
    min_length = 1
    highmatched = []
    k = -1
#    print  "Length of file" ,len(file1.readlines())
    highmatchedlines = []
    nonmatchedlines = []
    approvedlines = []

    #browse the sentences of the big corpus one by one
    for line1 in file1_src:
        line1_tgt = file1_tgt.readline()
        i=0
        k+=1
        file2.seek(0)
        
        # process src sentence
        line1_clean = line1.lower().strip()
        set1 = set(line1_clean.split())
        list1 = line1_clean.split()
        if min_length and len(list1) < min_length:
            print k, "sentence in src file too small: ", len(list1)
            continue
        if line1_clean in approvedlines:
            print k, "line already there in src"
            continue
        
        # process tgt sentence
        line1_tgt_clean = line1_tgt.lower().strip()
        set1_tgt = set(line1_tgt_clean.split())
        list1_tgt = line1_tgt_clean.split()
        if min_length and len(list1_tgt) < min_length:
            print k, "sentence in tgt too small: ", len(list1_tgt)
            continue
            
        approvedline = True
        
        line2 = file2.readline()
        
        #if line is not too small or dupped, compare it one by one with the sentences of the second set
        while approvedline and line2:
        
            line2_clean = line2.lower().strip()
#            print k, i  
            set2 = set(line2_clean.split())
            intersection = set2.intersection(set1)
            matched.append(len(intersection))
            try:
                overlap = (1.00*len(intersection))/len(set2)
            except:
                overlap = 0
            
            if overlap > threshold:
            #    highmatched.append((k, i, 1.00*len(intersection)/len(set2), line1, line2 ))
            #if line1_clean == line2_clean:
             
                print k, i, "overlap: ", 1.00*len(intersection)/len(set2)
                
                highmatched.append((k, i, 1.00*len(intersection)/len(set2), line1, line2 ))
                highmatchedlines.append(k)
                approvedline = False
                
            i+=1
            line2 = file2.readline()

        if approvedline: 
            filteredfile_src.write("{}".format(line1))
            approvedlines.append(approvedline)
            filteredfile_tgt.write("{}".format(line1_tgt))
                
        
  

    file1_src.close()
    file1_tgt.close()
    file2.close()

            
    
    filteredfile_src.close()
    filteredfile_tgt.close()


 
    for h in highmatched:
        h = [str(j) for j in h]
        print "\t".join(h)

    targetcount = set()
    for k,i,p,l1,l2 in highmatched:
        targetcount.add(i)
        #targetcount[i] = True #targetcount.setdefault(i, 0) + 1
    print (100.00*len(targetcount))/(1.00*len_file2) , "% of the test-set sentences were found in the training set"
    
    print 1.00*sum(matched)/len(matched)
