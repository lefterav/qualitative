import re
import sys

counter = 0

for line in sys.stdin:
    newline = ""
    for word in line.split(' '):
        if len(word) > 100:
            newline = newline + word[0:100] + " "
            counter +=1
        else:
            newline = newline + word  + " " 
    sys.stdout.write(newline)
sys.stderr.write("%d words trimmed" % counter) 
