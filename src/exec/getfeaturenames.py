from sys import argv

ratiofeatures = []
noratiofeatures = []
allfeatures = []

a = argv[1]
attlist = a.split('" ')
for att in attlist:
    att_name = att.split("=")[0]
    if att_name not in ["rank"] and not att_name.endswith("berkeley_tree"):
        allfeatures.append(att_name)
        if att_name.endswith("ratio"):
            ratiofeatures.append(att_name)
        else:
            noratiofeatures.append(att_name)
            
print "all features:\n", ",".join(allfeatures)
print "single features:\n", ",".join(noratiofeatures)
print "ratio features:\n", ",".join(ratiofeatures)
