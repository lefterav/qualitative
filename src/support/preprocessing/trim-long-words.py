import re
import sys

counter = 0

for line in sys.stdin:
    for word in line.split(' '):
        if len(word) > 100:
            line2 = re.sub(word, word[0:100], line)
            counter +=1
        else:
            line2 = line 
    sys.stdout.write(line2)
sys.stderr.write("%d words trimmed" % counter) 
