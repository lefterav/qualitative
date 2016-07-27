"""
Interface for feature generators, i.e. classes which handle the 
generation of features over the parallel objects. Any new featuregenerator
should implement languagefeaturegenerator.py (if it is language-specific)
or featuregenerator.py  (it is language-generic).
"""


def get_feature_generators(attribute_set):
    """
    Return the feature generators that are required to provide the features 
    in the given attribute set 
    """
    