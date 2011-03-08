import re
import sys

counter = 0

for line in sys.stdin:
    for word in line.split(' '):
        if len(word) > 100:
            line = re.sub(word, word[0:100], line)
            counter +=1
    sys.stdout.write(line)
sys.stderr.write("%d words trimmed" % counter) 
