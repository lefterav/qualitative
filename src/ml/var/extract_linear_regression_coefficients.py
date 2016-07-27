import cPickle as pickle
f=open('classifier.clsf')
classifier = pickle.load(f)
f.close()
w=open('classifier.dump.txt','w')
w.write(classifier.to_string())
    
w.close()
