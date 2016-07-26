import cPickle as pickle
f=open('classifier.clsf')
classifier = pickle.load(f)
f.close()
weights_aligned = zip(classifier.__dict__['domain'],classifier.__dict__['weights'][0])
weights_sorted = sorted(weights_aligned, key=lambda x: -abs(x[1]))
w=open('classifier.weights','w')

for feature, weight in weights_sorted:
    w.write('{}\t{}\n'.format(feature.name, weight))
    
w.close()
