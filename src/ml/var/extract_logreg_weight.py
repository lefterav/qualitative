from Orange.classification import logreg
import cPickle as pickle
f = open('classifier.clsf')
classifier = pickle.load(f)
f.close()
textfilename = "classifier.dump.txt"
f = open(textfilename, "w")
f.write(logreg.dump(classifier))
f.close()
