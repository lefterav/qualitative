#!/usr/bin/env python
import sys

prevId = ''
for line in sys.stdin:
    (id, e, scores, total) = line.split(' ||| ')
    if id != prevId:
        prevId = id
        print e
