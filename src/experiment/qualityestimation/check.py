'''
Created on 07 Mar 2012

@author: lefterav
'''

from suite import QualityEstimationSuite
import argparse 
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display progress of variable')

    directory = sys.argv[1]
    
    mysuite = QualityEstimationSuite()
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
            
        
        
        
        
