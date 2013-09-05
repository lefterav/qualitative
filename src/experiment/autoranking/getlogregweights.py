import cPickle
from Orange.classification import logreg
f=open('classifier.clsf','r')
c=cPickle.load(f)
f.close()
f=open('logreg.dump.log','w')
f.write(logreg.dump(c))
f.close()
