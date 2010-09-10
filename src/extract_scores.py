# -*- coding: utf-8 -*-
import codecs
import sys

def extract_length(string):
	return float(string.strip().split(',')[1].split()[0])

def extract_prob(string):
	return float(string.strip().split(',')[1].split()[1])

def extract_scores(file, out):
	lengthFlag = False
	length = 0
	probFlag = False
	prob = 0
	for line in file:
		if 'sentences' in line and 'words' in line and 'OOVs' in line:
			length = extract_length(line)
			lengthFlag = True
		elif 'zeroprobs' in line:
			prob = extract_prob(line)
			probFlag = True
		
		if lengthFlag and probFlag:
			score = float(prob/length)
			out.write('%.5f\n' % score)
			lengthFlag = False
			probFlag = False	


if __name__ == '__main__':
	input = codecs.open(sys.argv[1])
	out = codecs.open(sys.argv[1]+".scores", 'w', 'utf-8')
	extract_scores(input,out)
