from sys import argv

ratiofeatures = []
noratiofeatures = []
allfeatures = []
srcfeatures = []

a = argv[1]
attlist = a.split('" ')
for att in attlist:
    att_name = att.split("=")[0]
    if att_name not in ["rank"] and not att_name.endswith("berkeley-tree"):
        for i in range(1,3):
            att_name_pairwise = "tgt-%d_%s" % (i, att_name)
            allfeatures.append(att_name_pairwise)
            if att_name_pairwise.endswith("ratio"):
                ratiofeatures.append(att_name_pairwise)
            else:
                noratiofeatures.append(att_name_pairwise)

b = argv[2]
attlist = b.split('" ')
for att in attlist:
    att_name = att.split("=")[0]
    if att_name not in ["rank"] and not att_name.endswith("berkeley-tree"):
    
        att_name = att.split("=")[0]
        att_name_pairwise = "src_%s" % att_name
        srcfeatures.append(att_name_pairwise)


print "all features:\n", ",".join(allfeatures)
print "single features:\n", ",".join(noratiofeatures)
print "ratio features:\n", ",".join(ratiofeatures)
print "source features:\n", ",".join(srcfeatures)
