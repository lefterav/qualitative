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
                entries.append((feature, beta, abs(float(beta))))
        sorted_entries = sorted(entries, key=itemgetter(2), reverse=True)
        results[langpair][errcat] = sorted_entries

#header
print "\\begin{tabular}{|lr|lr|lr|} \n "
for langpair in langpairs:
    print "\\multicolumn{{6}}{{c}}{{ {} }} \\\\ \\hline".format(langpair),
    print

    print " & ".join(["\\multicolumn{{2}}{{|c|}}{{ {} }}".format(errcat) for errcat in error_categories])
    print " \\\\ \\hline"
    for i in range(0,10):
#        for langpair in langpairs:
        mytuples = []
        for errcat in error_categories:            
            mytuples.append(" & ".join(results[langpair][errcat][i][0:2]))
        print " & ".join(mytuples),            
        print " \\\\"
    print " \\hline \\multicolumn{6}{c}{} \\\\"
print "\\end{tabular}"        

resultsdict = {}
#make feature groups:
groups = {}
for langpair in langpairs:
    for errcat in error_categories:
        for name, prob, abs_prob in results[langpair][errcat]:
            group_name = name.split("-")[0]
            groups.setdefault(group_name, set()).add(name)
            


for langpair in langpairs:
    resultsdict[langpair] = {}
    for errcat in error_categories:
        resultsdict[langpair][errcat] = {}
        rank = 0
        for name, prob, abs_prob in results[langpair][errcat]:
            rank += 1
            resultsdict[langpair][errcat][name] = (prob, rank)



for errcat in error_categories:
    print "\\begin{table*} \n " 
    print "\\begin{tabular}{|lr|rr|rr|rr|rr|rr|rr|} \n " 
    print "\\multicolumn{{ {} }}{{c}}{{ {} }} \\\\ \\hline".format(len(langpairs), errcat),
    rank = 0
    #header
    items = []
    for langpair in langpairs:
        items.append ("\\multicolumn{{2}}{{c}}{{ {} }} ".format(langpair))
               
    print "{} \\\\ \\hline".format(" & ".join(items))
        
    for name, prob, abs_prob in results["all"][errcat]:
        rank += 1
        print "{} & {} &".format(name, prob),
        items = []
        for langpair in langpairs[1:]:
            try:
                prob, rank = resultsdict[langpair][errcat][name]
                items.append(str(prob))
                items.append(str(rank))
            except KeyError:
                items.extend([" "," "])
        print " & ".join(items),
        print " \\\\ "
        
    print "\\end{tabular}"
    print "\\end{table*}"    
        
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
        
    for name, prob, abs_prob in results["all"][errcat]:
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
                    prob, rank = resultsdict[langpair][errcat][name]
                    items.append(str(prob))
                    items.append(str(rank))
                except KeyError:
                    items.extend([" "," "])
            print " & ".join(items),
            print " \\\\ "
        print " \\hline "
        
        
            
        
        
    print "\\end{tabular}"
    print "\\end{table*}"  
