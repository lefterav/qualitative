#!/usr/bin/env python
import sys
import re
import os

(gizaLogFile, gizaPerpFile) = sys.argv[1:]

# Parameter 's' changed from '' to 'training.es.vcb'
paramPattern = re.compile("Parameter '([^']*)' changed from '([^']*)' to '([^']*)'")
modelTimePattern = re.compile("Entire ([^ ]+).* Training took: ([0-9]+) seconds")
totalTimePattern = re.compile("Entire Training took: ([0-9]+) seconds")
finishPattern = re.compile("Program Finished at: (.+)")

stats = []

for line in open(gizaLogFile):
    match = paramPattern.match(line)
    if match:
        param = match.group(1)
        orig = match.group(2)
        new = match.group(3)
        stats.append( (param, new) )

    match = modelTimePattern.match(line)
    if match:
        model = match.group(1)
        seconds = match.group(2)
        stats.append( (model, seconds) )

    match = totalTimePattern.match(line)
    if match:
        seconds = match.group(1)
        stats.append( ('TotalSecondsElapsed', seconds) )

    match = finishPattern.match(line)
    if match:
        time = match.group(1)
        stats.append( ('FinishedAt', time) )

model = ''

f = open(gizaPerpFile)
f.next() # Skip header row
for line in f:
    cols = line.split()
    newModel = cols[3]

    if model and newModel != model:
        key = 'Perplexity.%s' % model
        stats.append( (key, PP) )

        key = 'ViterbiPerplexity.%s' % model
        stats.append( (key, vitPP) )

    PP = cols[4]
    vitPP = cols[6]
    model = newModel

for key, value in stats:
    print '%s %s'%(key, value)
