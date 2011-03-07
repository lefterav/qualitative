import re
import sys

for line in sys.stdin:
    for word in line.split(' '):
        if len(word) > 100:
            line = re.sub(word, word[0:100], line)
    sys.stdout.write(line) 
