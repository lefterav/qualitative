import os
from operator import itemgetter

langpairs = ["all", "de-en", "de-fr", "de-es", "en-de", "fr-de", "es-de"]
error_categories = [
                    'missErr',
                    'extErr',
#                    'rLexErr',
                    'rRer',
#                    'hRer',  
#                    'biHper',
#                    'biRper',
#                    'rbRer',
#                    'hbRer',
#                    'bmissErr',
#                    'bextErr',
#                    'rbLexErr',
#                    'hbLexErr']
]

mypath="/share/taraxu/selection-mechanism/errorprediction/learning/langpairs_clean/{langpair}/ref_generic/tgt-1_{errcat}.logreg.dump.txt"

results={}

for langpair in langpairs:
    
    results[langpair] = {}
    
    for errcat in error_categories:
        filename = mypath.format(langpair=langpair, errcat=errcat)
        f = open(filename)
        readrows = False

        entries = []
        for line in f:
            if "Intercept" in line:
                readrows = True
                columns = line.strip().split()
                feature = columns[0]
                beta = columns[1]
                intercept = beta
            elif readrows:
                columns = line.strip().split()
                feature = columns[0].replace("tgt-1_", "").replace("_","-")
                beta = columns[1]
                p = columns[4]
                entries.append((feature, beta, abs(float(beta)), p))
        sorted_entries = sorted(entries, key=itemgetter(2), reverse=True)
        results[langpair][errcat] = sorted_entries

     

resultsdict = {}
#make feature groups:
groups = {}
for langpair in langpairs:
    for errcat in error_categories:
        for name, prob, abs_prob, p in results[langpair][errcat]:
            group_name = name.split("-")[0]
            groups.setdefault(group_name, set()).add(name)
            


for langpair in langpairs:
    resultsdict[langpair] = {}
    for errcat in error_categories:
        resultsdict[langpair][errcat] = {}
        rank = 0
        for name, prob, abs_prob, p in results[langpair][errcat]:
            rank += 1
            resultsdict[langpair][errcat][name] = (prob, p)




for errcat in error_categories:
    groups_done = set()
    print "\\begin{table*} \n " 
    print "\\begin{tabular}{|l|rr|rr|rr|rr|rr|rr|rr|} \n " 
    print "\\multicolumn{{ {} }}{{c}}{{ {} }} \\\\ \\hline".format(len(langpairs), errcat),
    rank = 0
    #header
    items = [""] #empty first header cell
    for langpair in langpairs:
        items.append ("\\multicolumn{{2}}{{|c|}}{{ {} }} ".format(langpair))
               
    print "{} \\\\ \\hline".format(" & ".join(items))
        
    for name, prob, abs_prob, p in results["all"][errcat]:
        group_name = name.split("-")[0]
        rank += 1
#        print "{} & {} &".format(name, prob),
        if group_name in groups_done:
            continue
        groups_done.add(group_name)
            
        for name in groups[group_name]:
            items = []
            items.append(name)
            
            for langpair in langpairs:
                try:
                    prob, p = resultsdict[langpair][errcat][name]
                    items.append(prob)
                    items.append(p)
                except KeyError:
                    items.extend([" "," "])                
                
            print " & ".join(items),
            print " \\\\ "
        print " \\hline "
        
        
            
        
        
    print "\\end{tabular}"
    print "\\end{table*}"  
