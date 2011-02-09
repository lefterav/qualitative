import random, sys, string

n = int(sys.argv[1]) #number of sentences to select
filename1 = sys.argv[2]
filename2 = sys.argv[3] 
minwords = int(sys.argv[4]) #sentences will be accepted if they have a minimum number of words

random.seed()

file1 = open(filename1, 'r')

# get the number of lines in the file
# assume that sanity check of two files has been done
filesize = sum(1 for line in file1)
file1.close()

file1 = open(filename1, 'r')
file2 = open(filename2, 'r')

outfile1 = open("%s.%d" % (filename1, n), 'w')
outfile2 = open("%s.%d" % (filename2, n), 'w')

i=0

manually_selected = [ 0,  4,   7,  8,  9, 16, 18, 19, 22, 23, 26, 28, 31, 32, 33, 38, 39, 41, 43, 47, 52, 55, 56, 57, 58, 60, 62, 63, 66, 70, 73, 74, 77, 78, 79, 80, 81, 87, 90, 91, 92, 93, 94, 95, 98,102,104,109,117,121,124,125, 126,129,132,133,135,136,137,138,139,140,141,147,149, 150,151,153,154,157,159,160,161,162,163,165,168,170, 173,174,175,176,179,184,187,188,190,192,195,200,203, 204,212 ] 

for line1 in file1:
    line2 = file2.readline()
    
    if len(line1.split(' ')) > minwords and string.count(line1, '.') == string.count(line2, '.') :
	if i in manually_selected:
	        outfile1.write(line1)
        	outfile2.write(line2) 
	i+=1 
  
#randnumbers = []

#for i in range(1, n):
#    randnumbers.append(random.randint(1,filesize-1))


