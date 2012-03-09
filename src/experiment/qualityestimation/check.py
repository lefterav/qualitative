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
    ta = mysuite.get_values_fix_params("./%s" % directory , 0, "RootMeanSqrErr")
    tb = mysuite.get_values_fix_params("./%s" % directory, 0, "MeanAvgErr")
    tc = mysuite.get_values_fix_params("./%s" % directory, 0 , "LargeErrPerc")
    td = mysuite.get_values_fix_params("./%s" % directory, 0 , "SmallErrPerc")
    te = mysuite.get_values_fix_params("./%s" % directory, 0 , "Interval")
    tf = mysuite.get_values_fix_params("./%s" % directory, 0 , "DeltaAvg")
    tg = mysuite.get_values_fix_params("./%s" % directory, 0 , "Spearman-Corr")
    tacc = mysuite.get_values_fix_params("./%s" % directory, 0 , "CA")
    tauc = mysuite.get_values_fix_params("./%s" % directory, 0 , "AUC")
    
    for a, b, c, ad, e, f, g, acc, auc, d, in zip(ta[0], tb[0], tc[0], td[0], te[0], tf[0], tg[0], tacc[0], tauc[0], ta[1]):
        output = [str(a), str(b), str(c), str(ad), str(e), str(f), str(g), str(acc), str(auc)]
        output.append(d['classifier'])
        output.append(d['att'])
        if d.has_key('filter_score_diff'):
            output.append(str(d['filter_score_diff']))
        if d.has_key('discretization'):
            output.append(str(d['discretization']))
        
        if d.has_key('CA'):
            output.append(str(d['CA']))
        if d.has_key('AUC'):
            output.append(str(d['AUC']))
        print "\t".join(output)
            
        
        
        
        
