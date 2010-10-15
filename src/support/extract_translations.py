import sys
import codecs

lucy = list(codecs.open(sys.argv[1], 'r', 'utf-8'))
moses = list(codecs.open(sys.argv[2], 'r', 'utf-8'))
list = zip(lucy,moses)
out = codecs.open('moses_out', 'w', 'utf-8')

for (x,y) in list:
	if x.startswith('*'):
		out.write(x)
		out.write(y)
		out.write('\n')



