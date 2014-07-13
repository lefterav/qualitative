'''
Created on 07 Mar 2012

@author: lefterav
'''

from suite import QualityEstimationSuite
import argparse 
import sys

"""
Gathers the WMT12 quality estimation results from the app folders created with python Experiment Suite
"""
        
    


    
def sort_values(mysuite, directory, rep, mode):
    """
    Parallelizes and aligned the vectors provided by the Experiment Suite API
    @param mysuite: instance of the Experiment Suite or subclass
    @type mysuite: L{ExperimentSuite}
    @param directory: the directory that will be searched for results. It needs to have the structure suported by Experiment Suite
    @type directory: str 
    @return: A dictionary with one entry per app. 
    The key of each entry is a tuple containing (attribute_set,classifier_name,discretization,filterscorediff) and 
    its value is a list of (float) values, respectively to their names entered in the list 'required_feature_names'
    """

    table = []
    if mode:
        print "Scores for regression"
        required_feature_names = ["RMSE", "MAE", "MSE", "RSE", "R2"]
    else:
        required_feature_names = ["RootMeanSqrErr", "MeanAvgErr", "LargeErrPerc", "SmallErrPerc", "interval1", "interval2", "DeltaAvg", "Spearman-Corr", "CA", "AUC"]
    
    for feature in required_feature_names:
        vector = mysuite.get_values_fix_params("./%s" % directory , rep, feature)
        table.append(vector[0])
    table.append(vector[1])
    
    indexed_table = {}
    
    for row in zip(*table):
        features = row[:-1]
        d = row[-1]
        
        features_dict = dict([(name, value) for name, value in zip(required_feature_names, features)])
        
        if d.has_key('filter_score_diff'):
            newkey = (d['classifier'],d['att'],d['filter_score_diff'])
        elif d.has_key('discretization'):
            newkey = (d['classifier'],d['att'],d['discretization'])
        else:
            newkey = (d['classifier'],d['att'])
                    
        try:
            features_dict['CA'] = "%.1f" % (features_dict['CA'][0] *100.0)
        except:
            features_dict['CA'] = "None"
        try:
            features_dict['AUC'] =  "%.1f" % (features_dict['AUC'][0] *100.0)
        except:
            features_dict['AUC'] = "None"

        indexed_table[newkey] = [features_dict[f] for f in required_feature_names]
        
    return indexed_table
    
    
def print_values_directory(mysuite, directory):
    """
    Obsolete method
    """
    ta = mysuite.get_values_fix_params("./%s" % directory , 1, "RootMeanSqrErr")
    tb = mysuite.get_values_fix_params("./%s" % directory, 1, "MeanAvgErr")
    tc = mysuite.get_values_fix_params("./%s" % directory, 1 , "LargeErrPerc")
    td = mysuite.get_values_fix_params("./%s" % directory, 1 , "SmallErrPerc")
    te = mysuite.get_values_fix_params("./%s" % directory, 1 , "interval1")
    te2 = mysuite.get_values_fix_params("./%s" % directory, 1 , "interval2")
    tf = mysuite.get_values_fix_params("./%s" % directory, 1 , "DeltaAvg")
    tg = mysuite.get_values_fix_params("./%s" % directory, 1 , "Spearman-Corr")
    tacc = mysuite.get_values_fix_params("./%s" % directory, 1 , "CA")
    tauc = mysuite.get_values_fix_params("./%s" % directory, 1 , "AUC")
    
    for a, b, c, ad, e, e2, f, g, acc, auc, d, in zip(ta[0], tb[0], tc[0], td[0], te[0], te2[0], tf[0], tg[0], tacc[0], tauc[0], ta[1]):
        
        try:
            current_acc = "%.1f" % (acc[0]*100.0)
        except:
            current_acc = "None"
        try:
            current_auc =  "%.1f" % (auc[0]*100.0)
        except:
            current_auc = "None"
        output = [str(a), str(b), str(c), str(ad), str(e), str(e2), str(f), str(g), current_acc, current_auc]
        output.append(d['classifier'])
        output.append(d['att'])
        if d.has_key('filter_score_diff'):
            output.append(str(d['filter_score_diff']))
        if d.has_key('discretization'):
            output.append(str(d['discretization']))
        
        print "\t".join(output)
            
        
if __name__ == '__main__':
    #parser = argparse.ArgumentParser()
    #parser.add_argument('directories', action='append' )
    #parser.add_argument('--rep', default = 1)
    #parser.add_argument('-c', dest='config')
    
    #parser.add_argument('--regression' , dest='mode', action='store_const', const=True, default = False)
    #print sys.argv 
    #args = parser.parse_args(sys.argv[3:])
    
    directory1 = './100/quality_estimation_development/'
    directory2 = False
    rep = 0 
    mode = True
    #rep = int(args.rep)
    try:
        directory2 = parser.directories[0]
    except: 
        pass
    
    mysuite = QualityEstimationSuite()
    rep = 0    
    dict1 = sort_values(mysuite, directory1, rep, mode)
    if directory2:
        dict2 = dict(sort_values(mysuite, directory2, args.mode))
    
    #by using dict1 as a reference, align each of its entries with the 
    #corresponding entry of dict2 (second directory)
    for key, scores1 in dict1.iteritems():
        print "\t".join([str(k) for k in key]),"\t",
        print "\t".join([str(v) for v in scores1]),"\t",
        try:
            scores2 = dict2[key]
            print "\t".join([str(v) for v in scores2])
        except:
            print
    
        
        
        
        

