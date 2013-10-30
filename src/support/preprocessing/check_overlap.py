'''
Split a parallel document into a training and a test set

Created on 9 Nov 2012

@author: Eleftherios Avramidis
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
    threshold = 0.8
    min_length = 1
    highmatched = []
    k = -1
#    print  "Length of file" ,len(file1.readlines())
    highmatchedlines = []
    nonmatchedlines = []
    approvedlines = []
    for line1 in file1_src:
        line1_tgt = file1_tgt.readline()
        i=0
        k+=1
        file2.seek(0)
        line1_clean = line1.lower().strip()
        set1 = set(line1_clean.split()) 
        if min_length and len(set1) < min_length:
            print k, "sentence too small: ", len(set1)
            continue
            
        if line1_clean in approvedlines:
            print k, "line already there"
            continue 
            
        approvedline = True
        
        line2 = file2.readline()
        
        while approvedline and line2:
        
            line2_clean = line2.lower().strip()
#            print k, i  
            set2 = set(line2_clean.split())
            intersection = set2.intersection(set1)
            matched.append(len(intersection))
            overlap = (1.00*len(intersection))/len(set2)
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
    print 1.00*sum(matched)/len(matched)
