'''
Retrieve selected attribute names and number from a run RFECV

Created on Jul 24, 2016

@author: lefterav
'''
import pickle
import sys
from sentence.parallelsentence import FeatureSet as AttributeSet



def get_selected_attributes(filename):
    model = pickle.load(open(filename))
    fs = model.featureselector
    attset = model.attribute_set.target_attribute_names
    selected = [name for name, mask in zip(attset, fs.support_) if mask]
    return selected

if __name__ == '__main__':
    print get_selected_attributes(sys.argv[1])
