import sys
import codecs

lucy = list(codecs.open(sys.argv[1], 'r', 'utf-8'))
moses = list(codecs.open(sys.argv[2], 'r', 'utf-8'))
list = zip(lucy,moses)
out = codecs.open('moses_out_phrasal', 'w', 'utf-8')

for (x,y) in list:
	items = x.strip().split('\t')
	if items[1] == 'True':
		out.write(items[0]+'\n')
		out.write(y)
		out.write('\n')



