import pickle
from collections import OrderedDict
import time
import os

"""
Draft script to retrieve LibLinear from the stored model,  and add them into the proper position in the repetitions logs, when they were not retrieved during the pipeline execution
"""

def get_weights_liblinear(model):
    attributes = OrderedDict()
    weights = list(model.learner.weights[0])
    attnames = [att.name for att in model.learner.domain]

    for attname, weight in zip(attnames, weights):
        if attname.startswith("N_"):
            attname = attname[2:]
        attributes["att_{}_weight".format(attname)] = weight
    return attributes
        
        
if __name__ == '__main__':
    for i in range(10):
        filename = "{}.model.dump".format(i)
        model = pickle.load(open(filename))
        backed_log_filename = "{}.log.{}.bak".format(i, time.strftime("%Y-%m-%d_%H-%M"))
        new_log_filename = "{}.log".format(i)

        os.rename(new_log_filename, backed_log_filename)
        old_log = open(backed_log_filename)
        new_log = open(new_log_filename, 'w')

        weights = get_weights_liblinear(model)
        #print " ".join(["{}:{}".format(k,v) for k,v in weights.iteritems()])
        i = 0
        for line in old_log:
            if i==1:
                print >>new_log, " ".join(["{}:{}".format(k,v) for k,v in weights.iteritems()])
            else:
                new_log.write(line)
            i+=1
        old_log.close()
        new_log.close()
        
        
    

