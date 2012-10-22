'''
Created on Sep 26, 2012

@author: jogin

This script converts txt inputs from testDataESEN directory (or tuningDataESEN) into .jcml format.
'''

import re
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from numpy import average, var, std, array


treeLabelsCompile = re.compile("CAT\s*([^ )]*)")

def lucy_analyze_trees(tree_string, prefix):
    #count number of each label
    labels = re.findall(treeLabelsCompile, tree_string)
    counts = {}
    for label in labels:
        label = "{}_count_{}".format(prefix, label)
        counts[label] = counts.setdefault(label, 0) + 1  
    #convert integers to strings (otherwise writing breaks
    counts = dict([(key, str(value)) for key, value in counts.iteritems()])
    return counts


# This variable contains either 'testDataESEN' or 'tuningDataESEN'.
# IT IS NECESSARY TO BE FILLED-IN!
selectDir = 'testDataESEN'

if selectDir == 'testDataESEN':
    path = '/share/taraxu/data/jcml/ml4hmt2012/testDataESEN/newstest2011.' # testDataESEN
    tgtFile4Annotation0 = '%ss4.en.annotation' % path # testDataESEN
if selectDir == 'tuningDataESEN':
    path = '/share/taraxu/data/jcml/ml4hmt2012/tuningDataESEN/20000.' # tuningDataESEN
    tgtFile4Annotation0_0 = '%ss4.en.annotation.0' % path # tuningDataESEN
    tgtFile4Annotation0_1 = '%ss4.en.annotation.1' % path # tuningDataESEN
    tgtFile4Annotation0_2 = '%ss4.en.annotation.2' % path # tuningDataESEN
    tgtFile4Annotation0_3 = '%ss4.en.annotation.3' % path # tuningDataESEN
    tgtFile4Annotation0_4 = '%ss4.en.annotation.4' % path # tuningDataESEN
srcFile = '%ses' % path
refFile = '%sref.en' % path
tgtFile1 = '%ss1.en' % path
tgtFile1Annotation0 = '%ss1.en.annotation.0' % path
tgtFile1Annotation1 = '%ss1.en.annotation.1' % path
tgtFile2 = '%ss2.en' % path
tgtFile2Annotation0 = '%ss2.en.annotation.0' % path
tgtFile2Annotation1 = '%ss2.en.annotation.1' % path
tgtFile3 = '%ss3.en' % path
tgtFile3Annotation0 = '%ss3.en.annotation' % path
tgtFile4 = '%ss4.en' % path

outputFilename = '%sjcml' % path

if __name__ == '__main__':

    source_file = open(srcFile, 'r')
    refFile = open(refFile, 'r')
    target_file_1 = open(tgtFile1, 'r')
    target_file_1_a_0 = open(tgtFile1Annotation0, 'r')
    target_file_1_a_1 = open(tgtFile1Annotation1, 'r')
    target_file_2 = open(tgtFile2, 'r')
    target_file_2_a_0 = open(tgtFile2Annotation0, 'r')
    target_file_2_a_1 = open(tgtFile2Annotation1, 'r')
    target_file_3 = open(tgtFile3, 'r')
    target_file_3_a_0 = open(tgtFile3Annotation0, 'r')
    target_file_4 = open(tgtFile4, 'r')
    if selectDir == 'testDataESEN':
        target_file_4_a_0 = open(tgtFile4Annotation0, 'r') # testDataESEN
    if selectDir == 'tuningDataESEN':
        target_file_4_a_0_0 = open(tgtFile4Annotation0_0, 'r') # tuningDataESEN
        target_file_4_a_0_1 = open(tgtFile4Annotation0_1, 'r') # tuningDataESEN
        target_file_4_a_0_2 = open(tgtFile4Annotation0_2, 'r') # tuningDataESEN
        target_file_4_a_0_3 = open(tgtFile4Annotation0_3, 'r') # tuningDataESEN
        target_file_4_a_0_4 = open(tgtFile4Annotation0_4, 'r') # tuningDataESEN

    # target sentence 1 - compilations
    reTagCompile = re.compile('(<.*?>)')

    # target sentence 2 - compilations
    unkWordsNoCompile = re.compile('<U\[.*?\]>')
    ambiguitiesNoCompile = re.compile('<A\[.*?\]>')
    analysisCompile = re.compile('<analysis>(.*?)</analysis>')
    transferCompile = re.compile('<transfer>(.*?)</transfer>')
    mirCompile = re.compile('<mir>(.*?)</mir>')
    generationCompile = re.compile('<generation>(.*?)</generation>')

    # target sentence 3 - compilations
    paramsCompile = re.compile('(\d+)..(\d+)](.*?)TRANSLATED AS:(.*?)WORD ALIGNED:(.*?)')
    reScoresCompile = re.compile('d: (-*\d+.\d+) w: (-*\d+.\d+) u: (-*\d+.\d+) d: (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) lm: (-*\d+.\d+) tm: (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+)')

    # target sentence 4 - compilations
    reSpanCompile = re.compile('\[(\d+)..(\d+)\]:')
    reBracketsCompile = re.compile('(\[\d+..\d+\]=[^ ]+)')
    ruleCompile = re.compile('\[\d+..\d+\]=[^ ]+\s+: (.*?->.*?) :.*?: pC=')
    alignmentCompile = re.compile('\[\d+..\d+\]=[^ ]+\s+: .*?->.*? :(.*?): pC=')
    repCCompile = re.compile('pC=(-*\d*.*\d+)')
    recCompile = re.compile('c=(-*\d*.*\d+) (-*\d*.*\d+)')
    reValuesCompile = re.compile('<<(.*?)>>')
    subderivStartCompile = re.compile('\[(\d+)..\d+\]')
    subderivEndCompile = re.compile('\[\d+..(\d+)\]')
    subderivHeadCompile = re.compile('\[\d+..\d+\]=([^ ]+)')
    
    
    parallelsentences = []
    i = 0
    nextString = ''
    iFile = 0
    
    for source_line in source_file:
        i+=1
        print i
        
        # get source sentence
        source_line = source_line.strip()
        source_sentence = SimpleSentence(source_line)
        
        # get reference sentence
        if refFile:
            reference_line = refFile.readline().strip()
            reference_sentence = SimpleSentence(reference_line)
        else:
            reference_sentence = None
       
        
        # get target sentence 1, it's annotation 0 and annotation 1
        target_line_1 = target_file_1.readline().strip()
        target_line_1_annotation_0 = target_file_1_a_0.readline().strip()
        target_line_1_annotation_1 = target_file_1_a_1.readline().strip()
        
        atts_1 = {}
        atts_1["s1_alignment"] = target_line_1_annotation_0
        atts_1["s1_generation"] = target_line_1_annotation_1
        atts_1["s1_untranslated"] = target_line_1_annotation_1.count("^@")
        atts_1["s1_unanalyzed"] = target_line_1_annotation_1.count("^*")
        atts_1["s1_unmorph"] = target_line_1_annotation_1.count("^#")
        atts_1["s1_joined"] = target_line_1_annotation_1.count("+")
        tagsDict = {}
        for tag in reTagCompile.findall(target_line_1_annotation_1):
            if tag in tagsDict: tagsDict[tag] += 1
            else: tagsDict[tag] = 1
        for key, value in tagsDict.items():
            atts_1["s1_count_%s" % key.strip('<>')] = str(value)
        atts_1["system"] = 's1'
        
        target_sentences = [SimpleSentence(target_line_1, atts_1)]
       
        
        # get target sentence 2, it's annotation 0 and annotation 1
        target_line_2 = target_file_2.readline().strip()
        target_line_2_annotation_0 = target_file_2_a_0.readline().strip()
        
        target_line_2_annotation_1 = ''
        while not target_line_2_annotation_1.count('</trees>'):
            target_line_2_annotation_1 += target_file_2_a_1.readline().strip() 
       
        atts_2 = {}
        atts_2["s2_verbose"] = target_line_2_annotation_0
        unkWordsNo = len(unkWordsNoCompile.findall(target_line_2_annotation_0))
        ambiguitiesNo = len(ambiguitiesNoCompile.findall(target_line_2_annotation_0))
        atts_2["s2_verbose_unk_words_No"] = str(unkWordsNo)
        atts_2["s2_verbose_ambiguities_No"] = str(ambiguitiesNo)
        atts_2["s2_analysis"] = analysisCompile.search(target_line_2_annotation_1).group(1)
        atts_2["s2_transfer"] = transferCompile.search(target_line_2_annotation_1).group(1)
        atts_2["s2_mir"] = mirCompile.search(target_line_2_annotation_1).group(1)
        atts_2["s2_generation"] = generationCompile.search(target_line_2_annotation_1).group(1)
        atts_2["s2_system"] = 's2'
        
        atts_2.update(lucy_analyze_trees(atts_2["s2_analysis"], "s2_analysis"))
        atts_2.update(lucy_analyze_trees(atts_2["s2_generation"], "s2_generation"))
        atts_2.update(lucy_analyze_trees(atts_2["s2_transfer"], "s2_transfer"))
        
        
        target_sentences.append(SimpleSentence(target_line_2, atts_2))
        
        
        # get target sentence 3 and it's annotation
        target_line_3 = target_file_3.readline().strip()
        target_line_3_annotation_0 = ''
        while not target_line_3_annotation_0.count('SCORES (UNWEIGHTED/WEIGHTED):'):
            target_line_3_annotation_0 += target_file_3_a_0.readline().strip()
        
        atts_3 = {}
        thd = target_line_3_annotation_0.split('SOURCE/TARGET SPANS:')[0].split('SOURCE: [')[1:]
        j = -1
        unknownAlignments = 0
        for word in thd:
            j += 1
            params = paramsCompile.search(word)
            beginNo = params.group(1)
            endNo = params.group(2)
            source = params.group(3).strip()
            target = params.group(4).strip()
            boolAlignmentUnk = False
            wordAligned = params.group(5).strip()
            if wordAligned:
                boolAlignmentUnk = True
                unknownAlignments += 1
                      
            atts_3["alignment_%s_source_span" % j] = '%s,%s' % (beginNo, endNo)
            atts_3["alignment_%s_source_string" % j] = source
            atts_3["alignment_%s_target_string" % j] = target
            atts_3["alignment_%s_unk" % j] = str(boolAlignmentUnk)

        atts_3["alignment_%s_unk_words" % j] = str(unknownAlignments)
            
            
        sts = target_line_3_annotation_0.split('SOURCE/TARGET SPANS:')[1].split('SCORES (UNWEIGHTED/WEIGHTED): ')[0].strip()
        atts_3["alignment_source_spans"] = sts.split('SOURCE: ')[1].split('TARGET:')[0].strip()
        atts_3["alignment_target_spans"] = sts.split('TARGET: ')[1].strip()
        
        sco = target_line_3_annotation_0.split('SCORES (UNWEIGHTED/WEIGHTED): ')[1].strip()
        reScores = reScoresCompile.search(sco)
        atts_3["scores_d"] = reScores.group(1).strip()
        atts_3["scores_w"] = reScores.group(2).strip()
        atts_3["scores_u"] = reScores.group(3).strip()
        atts_3["scores_d1"] = reScores.group(4).strip()
        atts_3["scores_d2"] = reScores.group(5).strip()
        atts_3["scores_d3"] = reScores.group(6).strip()
        atts_3["scores_d4"] = reScores.group(7).strip()
        atts_3["scores_d5"] = reScores.group(8).strip()
        atts_3["scores_lm"] = reScores.group(9).strip()
        atts_3["scores_tm1"] = reScores.group(10).strip()
        atts_3["scores_tm2"] = reScores.group(11).strip()
        atts_3["scores_tm3"] = reScores.group(12).strip()
        atts_3["scores_tm4"] = reScores.group(13).strip()
        atts_3["scores_tm5"] = reScores.group(14).strip()
        
        atts_3["system"] = 's3'
        
        target_sentences.append(SimpleSentence(target_line_3, atts_3))


        # get target sentence 4 and it's annotation
        target_line_4 = target_file_4.readline().strip()
        
        if selectDir == 'tuningDataESEN':
            target_files = [target_file_4_a_0_0, target_file_4_a_0_1, target_file_4_a_0_2, target_file_4_a_0_3, target_file_4_a_0_4]
        target_line_4_annotation_0 = nextString
        while 1:
            if selectDir == 'testDataESEN': line = target_file_4_a_0.readline().strip()
            if selectDir == 'tuningDataESEN': line = target_files[iFile].readline().strip()            
            if line and not line.count('Trans Opt %s' % (i%4000)):
                target_line_4_annotation_0 += line
            elif not line: # detect end of file
                iFile += 1
                nextString = ''
                break
            else: # detect end of sentence
                nextString = line
                break
        
        atts_4 = {}
        z = -1
        
        list_span_len = []
        list_subderivations = []
        list_subderivation_len = []
        list_pC = []
        list_c1 = []
        list_c2 = []
        list_x = []

        for transOpt in target_line_4_annotation_0.split('Trans Opt ')[1:]:
            z += 1
            reSpan = reSpanCompile.search(transOpt)
            brackets = reBracketsCompile.findall(transOpt)
            subderivationsNo = len(brackets)
            
            rule = ruleCompile.search(transOpt).group(1).strip()
            alignment = alignmentCompile.search(transOpt).group(1).strip()
        
            repC = repCCompile.search(transOpt)

            rec = recCompile.search(transOpt)
            reValues = reValuesCompile.search(transOpt).group(1).split(', ')
            
            span_start = reSpan.group(1)
            span_end = reSpan.group(2)
            span_len = int(span_end) - int(span_start)            
            list_span_len.append(span_len)
            
            subderivations = subderivationsNo
            list_subderivations.append(subderivations)
            
#            atts_4["deriv_%s_span_start" % z] = reSpan.group(1)
#            atts_4["deriv_%s_span_end" % z] = reSpan.group(2)
#            atts_4["deriv_%s_subderivations" % z] = str(subderivationsNo)
            subderiv_span_lens = []
            for y in range(len(brackets)):
                subderiv_span_start  = subderivStartCompile.search(brackets[y]).group(1)
#                atts_4["deriv_%s_subderiv_%s_span_start" % (z, y)] = subderivStartCompile.search(brackets[y]).group(1)
                subderiv_span_end = subderivEndCompile.search(brackets[y]).group(1)
                subderiv_span_len = int(subderiv_span_start) - int(subderiv_span_end)
                subderiv_span_lens.append(subderiv_span_len)
            
            list_subderivation_len.append(average(subderiv_span_lens))
            
#                atts_4["deriv_%s_subderiv_%s_span_end" % (z, y)] = subderivEndCompile.search(brackets[y]).group(1)
#                atts_4["deriv_%s_subderiv_%s_head" % (z, y)] =  subderivHeadCompile.search(brackets[y]).group(1)
#            atts_4["deriv_%s_rule" % z] = rule
#            atts_4["deriv_%s_alignment" % z] = alignment
            pC = repC.group(1)
            list_pC.append(pC)
#            atts_4["deriv_%s_pC" % z] = repC.group(1)
            c1 = rec.group(1)
            list_c1.append(c1)
#            atts_4["deriv_%s_c1" % z] = rec.group(1)    
            c2 = rec.group(2)
            list_c2.append(c2)
#            atts_4["deriv_%s_c2" % z] = rec.group(2)
            X = {}

            for x in range(1,9):
                X[x](reValues[x-1])
            list_x.append(X)
        
        atts_4["s4_span_len_avg"] = average(list_span_len)
        atts_4["s4_span_len_var"] = var(list_span_len)
        atts_4["s4_span_len_std"] = std(list_span_len)
        
        atts_4["s4_subderivations_avg"] = average(list_subderivations)
        
        atts_4["s4_subderivation_len_avg"] = average(list_subderivation_len)
        
        atts_4["s4_pC_avg"] = average(list_pC)
        
        atts_4["s4_c1_avg"] = average(list_c1)
        
        atts_4["s4_c2_avg"] = average(list_c1)
        
        for x in list_x:
             
              
        
        
        
        
            
        #now get averages, variations and standard deviations from the collected things
                
        atts_4["system"] = 's4'

        target_sentences.append(SimpleSentence(target_line_4, atts_4))


        # parallel sentence attributes
        ps_atts =  {"langsrc" : 'es' ,
                     "langtgt" : 'en' ,
                     "testset" : 'newstest2011' ,
                     "id" : str(i)}
        
        ps = ParallelSentence(source_sentence, target_sentences, reference_sentence, ps_atts)
        parallelsentences.append(ps)
    
    Parallelsentence2Jcml(parallelsentences).write_to_file(outputFilename)
