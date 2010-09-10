# -*- coding: utf-8 -*-

import sys
import codecs

def create_evaluation(judgments):
    total = 0
    sum = 0
    for line in judgments:
        fields = line.split(',')
        system1 = fields[7]
        system2 = fields[9]
        system3 = fields[11]
        system4 = fields[13]
        system5 = fields[15]
        rank1 = int(fields[16])
        rank2 = int(fields[17])
        rank3 = int(fields[18])
        rank4 = int(fields[19])
        rank5 = int(fields[20])
        entries = []
	entries.append(rank1)
	entries.append(rank2)
	entries.append(rank3)
	entries.append(rank4)
	entries.append(rank5)
        if 1 not in entries:
		if -1 in entries:
			entries2 = []
			for x in entries:
				if x != -1:
					entries2.append(x)
			if len(entries2) > 0:
				index = min(entries2)
				diff = index -1
				new_entries = []
				for x in entries:
					if x != -1:
						new_entries.append(x - diff)
					else:
						new_entries.append(x)
		else:
	     		index = min(entries)
			diff = index - 1
			new_entries = []
			for x in entries:
				new_entries.append(x - diff)
			print entries
			print new_entries
			entries = new_entries
	total += 1
	if system1 == 'dfki':
		if entries[0] != -1:
			sum += entries[0]
	if system2 == 'dfki':
		if entries[1] != -1:
			sum += entries[1]
	if system3 == 'dfki':
		if entries[2] != -1:
			sum += entries[2]
	if system4 == 'dfki':
		if entries[3] != -1:
			sum += entries[3]
	if system5 == 'dfki':
		if entries[4] != -1:
			sum += entries[4]
	
    return float(sum/total)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'USAGE: %s JUDGMENTS.CSV' % sys.argv[0]
    else:
        input = codecs.open(sys.argv[1], 'r', 'utf-8')
        result = create_evaluation(input)
	print result
