'''
Created on Sep 26, 2012

@author: jogin

This script converts txt inputs from testDataESEN directory (or tuningDataESEN) into .jcml format.
There are 4 classes - Apertium, Lucy, Moses and Moses2.
'''

from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from numpy import average, var, std, array
import re
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
import sys


class Moses2FeatureGenerator():
    '''
    @param inputPath: path to directory with input files
    @param outputFile: path to output file including output filename
    @param langsrc: abbreviation of source language
    @param langtgt: abbreviation of target language
    @param testset: testset name (e.g. "newstest2011" or "20000")
    @param selectDir: name of directory with input files (either testDataESEN or tuningDataESEN)
    '''
    def __init__(self, inputPath, outputFile, langsrc, langtgt, testset, selectDir):
        # Moses2 - compilations    
        self.reSpanCompile = re.compile('\[(\d+)..(\d+)\]:')
        self.reBracketsCompile = re.compile('(\[\d+..\d+\]=[^ ]+)')
        self.ruleCompile = re.compile('\[\d+..\d+\]=[^ ]+\s+: (.*?->.*?) :.*?: pC=')
        self.alignmentCompile = re.compile('\[\d+..\d+\]=[^ ]+\s+: .*?->.*? :(.*?): pC=')
        self.repCCompile = re.compile('pC=([^ ,]*)')
        self.recCompile = re.compile('c=([^ ,]*) ([^ ,<]*)')
        self.reValuesCompile = re.compile('<<(.*?)>>')
        self.subderivStartCompile = re.compile('\[(\d+)..\d+\]')
        self.subderivEndCompile = re.compile('\[\d+..(\d+)\]')
        self.subderivHeadCompile = re.compile('\[\d+..\d+\]=([^ ]+)')
        self.selectDir = selectDir
        self.iFile = 0

        self.nextString = ''
        parallelSentences = []
        i = 0
        while 1:
            i+=1
            print i
            
            srcLine, refLine, tgtLine, annoLine = self.read_line(i, inputPath, testset)
            if not srcLine: break # end loop if no more source sentence
            
            scoreDict, attrs = self.process_annotations(annoLine)
            scoreDict = self.analyse_features(i, scoreDict, attrs)
            
            srcSent, refSent, tgtSent = self.process_sentences(srcLine, refLine, tgtLine, scoreDict)
        
            # parallel sentence attributes
            psAtts =  {"langsrc" : langsrc, "langtgt" : langtgt, "testset" : testset, "id" : str(i)}
            
            ps = ParallelSentence(srcSent, tgtSent, refSent, psAtts)
            parallelSentences.append(ps)
    
        Parallelsentence2Jcml(parallelSentences).write_to_file(outputFile)


    '''
    Read input files and for each call return 1 line from each file. 
    @param i: number of sentence (line)
    @param inputPath: path to directory where input files are
    @param testset: testset name (e.g. "newstest2011" or "20000")
    @return srcLine: source sentence (line)
    @return refLine: reference sentence (line)
    @return tgtLine: target sentence (line)
    @return annoLine: 1 line in annotation file
    '''
    def read_line(self, i, inputPath, testset):
        if i == 1:
            srcSnts = '%s%s.es' % (inputPath, testset)
            refSnts = '%s%s.ref.en' % (inputPath, testset)
            tgtSnts = '%s%s.s4.en' % (inputPath, testset)
            
            if self.selectDir == 'testDataESEN':
                annotation = '%s%s.s4.en.annotation' % (inputPath, testset)
            elif self.selectDir == 'tuningDataESEN':
                annotation0 = '%s%s.s4.en.annotation.0' % (inputPath, testset)
                annotation1 = '%s%s.s4.en.annotation.1' % (inputPath, testset)
                annotation2 = '%s%s.s4.en.annotation.2' % (inputPath, testset)
                annotation3 = '%s%s.s4.en.annotation.3' % (inputPath, testset)
                annotation4 = '%s%s.s4.en.annotation.4' % (inputPath, testset)
            else:
                sys.exit('Param selectDir must be either "testDataESEN" or "tunningDataESEN".')
            
            self.srcFile = open(srcSnts, 'r')
            self.refFile = open(refSnts, 'r')
            self.tgtFile = open(tgtSnts, 'r')
            if self.selectDir == 'testDataESEN':
                self.annoFile0 = open(annotation, 'r') # testDataESEN
                self.annoFile1 = None # empty
                self.annoFile2 = None # empty
                self.annoFile3 = None # empty
                self.annoFile4 = None # empty
            if self.selectDir == 'tuningDataESEN':
                self.annoFile0 = open(annotation0, 'r') # tuningDataESEN
                self.annoFile1 = open(annotation1, 'r') # tuningDataESEN
                self.annoFile2 = open(annotation2, 'r') # tuningDataESEN
                self.annoFile3 = open(annotation3, 'r') # tuningDataESEN
                self.annoFile4 = open(annotation4, 'r') # tuningDataESEN
        
        # get source sentence
        srcLine = self.srcFile.readline().strip()
        
        # get reference sentence
        if self.refFile:
            refLine = self.refFile.readline().strip()
        else:
            refLine = None
       
        # get target sentence
        tgtLine = self.tgtFile.readline().strip()
       
        # get annotations
        if self.selectDir == 'tuningDataESEN':
            annoFiles = [self.annoFile0, self.annoFile1, self.annoFile2, self.annoFile3, self.annoFile4]
        annoLine = self.nextString
        while 1:
            if self.selectDir == 'testDataESEN': line = self.annoFile0.readline().strip()
            if self.selectDir == 'tuningDataESEN': line = annoFiles[self.iFile].readline().strip()            
            if line and not line.count('Trans Opt %s' % (i%4000)):
                annoLine += line
            elif not line: # detect end of file
                self.iFile += 1
                self.nextString = ''
                break
            else: # detect end of sentence
                self.nextString = line
                break
        return srcLine, refLine, tgtLine, annoLine
        
        
    '''
    Convert sentences (lines) into SimpleSentence objects. 
    @param srcLine: source sentence (line)
    @param refLine: reference sentence (line)
    @param tgtLine: target sentence (line)
    @param scoreDict: dictionary with parsed scores
    @return srcSent: source sentence as SimpleSentence object
    @return refSent: reference sentence as SimpleSentence object
    @return tgtSent: target sentence with scores as SimpleSentence object
    '''
    def process_sentences(self, srcLine, refLine, tgtLine, scoreDict):
        srcSent = SimpleSentence(srcLine)
        if refLine: refSent = SimpleSentence(refLine)
        else: refSent = None
        tgtSent = [SimpleSentence(tgtLine, scoreDict)]
        return srcSent, refSent, tgtSent
    
    
    '''
    Parse input files.
    @param annoFile: annotation file
    @return dict of features
    ''' 
    def process_annotations(self, annoLine):
        scoreDict = {}
        scoreDict["system"] = 's4-Moses2'

        z = -1        
        list_span_len = []
        list_subderivations = []
        list_subderivation_len = []
        list_pC = []
        list_c1 = []
        list_c2 = []
        list_x = []

        for transOpt in annoLine.split('Trans Opt ')[1:]:
            z += 1
            reSpan = self.reSpanCompile.search(transOpt)
            brackets = self.reBracketsCompile.findall(transOpt)
            subderivationsNo = len(brackets)
            
            rule = self.ruleCompile.search(transOpt).group(1).strip()
            alignment = self.alignmentCompile.search(transOpt).group(1).strip()
        
            repC = self.repCCompile.search(transOpt)

            rec = self.recCompile.search(transOpt)
            reValues = self.reValuesCompile.search(transOpt).group(1).split(', ')
            
            span_start = reSpan.group(1)
            span_end = reSpan.group(2)
            span_len = int(span_end) - int(span_start)            
            list_span_len.append(span_len)
            
            subderivations = subderivationsNo
            list_subderivations.append(subderivations)

            subderiv_span_lens = []
            for y in range(len(brackets)):
                subderiv_span_start  = self.subderivStartCompile.search(brackets[y]).group(1)
                subderiv_span_end = self.subderivEndCompile.search(brackets[y]).group(1)
                subderiv_span_len = int(subderiv_span_start) - int(subderiv_span_end)
                subderiv_span_lens.append(subderiv_span_len)
            
            list_subderivation_len.append(average(subderiv_span_lens))
            pC = float(repC.group(1))
            list_pC.append(pC)
            c1 = float(rec.group(1))
            list_c1.append(c1)    
            c2 = float(rec.group(2))
            list_c2.append(c2)
            X = {}
            for x in range(1,9):
                X[x] = reValues[x-1]
            list_x.append(X)
            
        scoreDict["derivations"] = z    
        attrs = (list_span_len, list_subderivations, list_subderivation_len, list_pC, list_c1, list_c2, list_x)
        return scoreDict, attrs 
    '''    
    @param i: number of sentence (line)
    @param scoreDict: dictionary with parsed scores
    @param attrs: list of parsed attributes
    Compute scores from input parsed data.
    @return scoreDict: updated dictionary with computed scores
    '''
    def analyse_features(self, i, scoreDict, attrs):
        #now get averages, variations and standard deviations from the collected things
        list_span_len = attrs[0]
        list_subderivations = attrs[1]
        list_subderivation_len = attrs[2]
        list_pC = attrs[3]
        list_c1 = attrs[4]
        list_c2 = attrs[5]
        list_x = attrs[6]
        
        scoreDict["span_len_avg"] = average(list_span_len)
        scoreDict["span_len_var"] = var(list_span_len)
        scoreDict["span_len_std"] = std(list_span_len)
        
        scoreDict["subderivations_avg"] = average(list_subderivations)
        scoreDict["subderivations_var"] = var(list_subderivations)
        scoreDict["subderivations_std"] = std(list_subderivations)
        
        scoreDict["subderivation_len_avg"] = average(list_subderivation_len)
        scoreDict["subderivation_len_var"] = var(list_subderivation_len)
        scoreDict["subderivation_len_std"] = std(list_subderivation_len)
        
        scoreDict["pC_avg"] = average(list_pC)
        scoreDict["pC_var"] = var(list_pC)
        scoreDict["pC_std"] = std(list_pC)
        
        scoreDict["c1_avg"] = average(list_c1)
        scoreDict["c1_var"] = var(list_c1)
        scoreDict["c1_std"] = std(list_c1)                
        
        scoreDict["c2_avg"] = average(list_c2)
        scoreDict["c2_var"] = var(list_c2)
        scoreDict["c2_std"] = std(list_c2)                
        
        for l in xrange (1,9):
            col = [float(x[l]) for x in list_x]
            scoreDict["x{}_avg".format(i)] = average(col)
        return scoreDict

        
class MosesFeatureGenerator():
    '''
    @param inputPath: path to directory with input files
    @param outputFile: path to output file including output filename
    @param langsrc: abbreviation of source language
    @param langtgt: abbreviation of target language
    @param testset: testset name (e.g. "newstest2011" or "20000")
    '''
    def __init__(self, inputPath, outputFile, langsrc, langtgt, testset):
        # Moses - compilations
        self.paramsCompile = re.compile('(\d+)..(\d+)](.*?)TRANSLATED AS:(.*?)WORD ALIGNED:(.*?)')
        self.reScoresCompile = re.compile('d: (-*\d+.\d+) w: (-*\d+.\d+) u: (-*\d+.\d+) d: (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) lm: (-*\d+.\d+) tm: (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+)')

        parallelSentences = []
        i = 0
        while 1:
            i+=1
            print i
            
            srcLine, refLine, tgtLine, annoLine = self.read_line(i, inputPath, testset)
            if not srcLine: break # end loop if no more source sentence
            
            scoreDict = self.process_annotations(annoLine)
            scoreDict = self.analyse_features(scoreDict)
            
            srcSent, refSent, tgtSent = self.process_sentences(srcLine, refLine, tgtLine, scoreDict)
        
            # parallel sentence attributes
            psAtts =  {"langsrc" : langsrc, "langtgt" : langtgt, "testset" : testset, "id" : str(i)}
            
            ps = ParallelSentence(srcSent, tgtSent, refSent, psAtts)
            parallelSentences.append(ps)
    
        Parallelsentence2Jcml(parallelSentences).write_to_file(outputFile)


    '''
    Read input files and for each call return 1 line from each file. 
    @param i: number of sentence (line)
    @param inputPath: path to directory where input files are
    @param testset: testset name (e.g. "newstest2011" or "20000")
    @return srcLine: source sentence (line)
    @return refLine: reference sentence (line)
    @return tgtLine: target sentence (line)
    @return annoLine: 1 line in annotation file
    '''
    def read_line(self, i, inputPath, testset):
        if i == 1:
            srcSnts = '%s%s.es' % (inputPath, testset)
            refSnts = '%s%s.ref.en' % (inputPath, testset)
            tgtSnts = '%s%s.s3.en' % (inputPath, testset)
            annotation = '%s%s.s3.en.annotation' % (inputPath, testset)
            
            self.srcFile = open(srcSnts, 'r')
            self.refFile = open(refSnts, 'r')
            self.tgtFile = open(tgtSnts, 'r')
            self.annoFile = open(annotation, 'r')
                
        # get source sentence
        srcLine = self.srcFile.readline().strip()
        
        # get reference sentence
        if self.refFile:
            refLine = self.refFile.readline().strip()
        else:
            refLine = None
       
        # get target sentence
        tgtLine = self.tgtFile.readline().strip()
       
        # get annotations
        annoLine = ''
        while srcLine and not annoLine.count('SCORES (UNWEIGHTED/WEIGHTED):'):
            annoLine += self.annoFile.readline().strip()
        return srcLine, refLine, tgtLine, annoLine
    
    
    '''
    Convert sentences (lines) into SimpleSentence objects. 
    @param srcLine: source sentence (line)
    @param refLine: reference sentence (line)
    @param tgtLine: target sentence (line)
    @param scoreDict: dictionary with parsed scores
    @return srcSent: source sentence as SimpleSentence object
    @return refSent: reference sentence as SimpleSentence object
    @return tgtSent: target sentence with scores as SimpleSentence object
    '''
    def process_sentences(self, srcLine, refLine, tgtLine, scoreDict):
        srcSent = SimpleSentence(srcLine)
        if refLine: refSent = SimpleSentence(refLine)
        else: refSent = None
        tgtSent = [SimpleSentence(tgtLine, scoreDict)]
        return srcSent, refSent, tgtSent
    
    '''
    Parse input file.
    @param annoFile: annotation file
    @return dict of features
    ''' 
    def process_annotations(self, annoLine):
        scoreDict = {}
        scoreDict["system"] = 's3-Moses'
        
        scoreDict = {}
        thd = annoLine.split('SOURCE/TARGET SPANS:')[0].split('SOURCE: [')[1:]
        j = -1
        unknownAlignments = 0
        for word in thd:
            j += 1
            params = self.paramsCompile.search(word)
            beginNo = params.group(1)
            endNo = params.group(2)
            source = params.group(3).strip()
            target = params.group(4).strip()
            boolAlignmentUnk = False
            wordAligned = params.group(5).strip()
            if wordAligned:
                boolAlignmentUnk = True
                unknownAlignments += 1
                      
            scoreDict["alignment_%s_source_span" % j] = '%s,%s' % (beginNo, endNo)
            scoreDict["alignment_%s_source_string" % j] = source
            scoreDict["alignment_%s_target_string" % j] = target
            scoreDict["alignment_%s_unk" % j] = str(boolAlignmentUnk)

        scoreDict["alignment_%s_unk_words" % j] = str(unknownAlignments)
            
            
        sts = annoLine.split('SOURCE/TARGET SPANS:')[1].split('SCORES (UNWEIGHTED/WEIGHTED): ')[0].strip()
        scoreDict["alignment_source_spans"] = sts.split('SOURCE: ')[1].split('TARGET:')[0].strip()
        scoreDict["alignment_target_spans"] = sts.split('TARGET: ')[1].strip()
        
        sco = annoLine.split('SCORES (UNWEIGHTED/WEIGHTED): ')[1].strip()
        reScores = self.reScoresCompile.search(sco)
        scoreDict["scores_d"] = reScores.group(1).strip()
        scoreDict["scores_w"] = reScores.group(2).strip()
        scoreDict["scores_u"] = reScores.group(3).strip()
        scoreDict["scores_d1"] = reScores.group(4).strip()
        scoreDict["scores_d2"] = reScores.group(5).strip()
        scoreDict["scores_d3"] = reScores.group(6).strip()
        scoreDict["scores_d4"] = reScores.group(7).strip()
        scoreDict["scores_d5"] = reScores.group(8).strip()
        scoreDict["scores_lm"] = reScores.group(9).strip()
        scoreDict["scores_tm1"] = reScores.group(10).strip()
        scoreDict["scores_tm2"] = reScores.group(11).strip()
        scoreDict["scores_tm3"] = reScores.group(12).strip()
        scoreDict["scores_tm4"] = reScores.group(13).strip()
        scoreDict["scores_tm5"] = reScores.group(14).strip()
        return scoreDict
       
        
    '''
    '''    
    def analyse_features(self, scoreDict):
        return scoreDict


class LucyFeatureGenerator():
    '''
    @param inputPath: path to directory with input files
    @param outputFile: path to output file including output filename
    @param langsrc: abbreviation of source language
    @param langtgt: abbreviation of target language
    @param testset: testset name (e.g. "newstest2011" or "20000")
    '''
    def __init__(self, inputPath, outputFile, langsrc, langtgt, testset):
        # Lucy - compilations
        self.unkWordsNoCompile = re.compile('<U\[.*?\]>')
        self.ambiguitiesNoCompile = re.compile('<A\[.*?\]>')
        self.analysisCompile = re.compile('<analysis>(.*?)</analysis>')
        self.transferCompile = re.compile('<transfer>(.*?)</transfer>')
        self.mirCompile = re.compile('<mir>(.*?)</mir>')
        self.generationCompile = re.compile('<generation>(.*?)</generation>')
        self.treeLabelsCompile = re.compile("CAT\s*([^ )]*)")
        
        parallelSentences = []
        i = 0
        while 1:
            i+=1
            print i
            
            srcLine, refLine, tgtLine, annoLine0, annoLine1 = self.read_line(i, inputPath, testset)
            if not srcLine: break # end loop if no more source sentence
            
            scoreDict = self.process_annotations(annoLine0, annoLine1)
            scoreDict = self.analyse_features(scoreDict)
            
            srcSent, refSent, tgtSent = self.process_sentences(srcLine, refLine, tgtLine, scoreDict)
        
            # parallel sentence attributes
            psAtts =  {"langsrc" : langsrc, "langtgt" : langtgt, "testset" : testset, "id" : str(i)}
            
            ps = ParallelSentence(srcSent, tgtSent, refSent, psAtts)
            parallelSentences.append(ps)
        
        Parallelsentence2Jcml(parallelSentences).write_to_file(outputFile)
        del self.srcFile
        del self.refFile
        del self.tgtFile
        del self.annoFile0
        del self.annoFile1


    '''
    Read input files and for each call return 1 line from each file. 
    @param i: number of sentence (line)
    @param inputPath: path to directory where input files are
    @param testset: testset name (e.g. "newstest2011" or "20000")
    @return srcLine: source sentence (line)
    @return refLine: reference sentence (line)
    @return tgtLine: target sentence (line)
    @return annoLine0: 1 line in annotation file 1
    @return annoLine1: 1 line in annotation file 2
    '''
    def read_line(self, i, inputPath, testset):
        if i == 1:
            srcSnts = '%s%s.es' % (inputPath, testset)
            refSnts = '%s%s.ref.en' % (inputPath, testset)
            tgtSnts = '%s%s.s2.en' % (inputPath, testset)
            annotation0 = '%s%s.s2.en.annotation.0' % (inputPath, testset)
            annotation1 = '%s%s.s2.en.annotation.1' % (inputPath, testset)
            
            self.srcFile = open(srcSnts, 'r')
            self.refFile = open(refSnts, 'r')
            self.tgtFile = open(tgtSnts, 'r')
            self.annoFile0 = open(annotation0, 'r')
            self.annoFile1 = open(annotation1, 'r')

        # get source sentence
        srcLine = self.srcFile.readline().strip()
        
        # get reference sentence
        if self.refFile:
            refLine = self.refFile.readline().strip()
        else:
            refLine = None
       
        # get target sentence
        tgtLine = self.tgtFile.readline().strip()

        # get annotations
        annoLine0 = self.annoFile0.readline().strip()
        
        annoLine1 = ''
        while srcLine and not annoLine1.count('</trees>'): 
            annoLine1 += self.annoFile1.readline().strip()

        return srcLine, refLine, tgtLine, annoLine0, annoLine1


    '''
    Convert sentences (lines) into SimpleSentence objects. 
    @param srcLine: source sentence (line)
    @param refLine: reference sentence (line)
    @param tgtLine: target sentence (line)
    @param scoreDict: dictionary with parsed scores
    @return srcSent: source sentence as SimpleSentence object
    @return refSent: reference sentence as SimpleSentence object
    @return tgtSent: target sentence with scores as SimpleSentence object
    '''
    def process_sentences(self, srcLine, refLine, tgtLine, scoreDict):
        srcSent = SimpleSentence(srcLine)
        if refLine: refSent = SimpleSentence(refLine)
        else: refSent = None
        tgtSent = [SimpleSentence(tgtLine, scoreDict)]
        return srcSent, refSent, tgtSent
    

    '''
    Parse input files.
    @param annoFile0: 1st annotation file
    @param annoFile1: 2nd annotation file
    @return dict of features
    '''
    def process_annotations(self, annoLine0, annoLine1):
        scoreDict = {}
        scoreDict["system"] = 's2-Lucy'
       
        scoreDict["verbose"] = annoLine0
        unkWordsNo = len(self.unkWordsNoCompile.findall(annoLine0))
        ambiguitiesNo = len(self.ambiguitiesNoCompile.findall(annoLine0))
        scoreDict["verbose_unk_words_No"] = str(unkWordsNo)
        scoreDict["verbose_ambiguities_No"] = str(ambiguitiesNo)
        scoreDict["analysis"] = self.analysisCompile.search(annoLine1).group(1)
        scoreDict["transfer"] = self.transferCompile.search(annoLine1).group(1)
        scoreDict["mir"] = self.mirCompile.search(annoLine1).group(1)
        scoreDict["generation"] = self.generationCompile.search(annoLine1).group(1)
        return scoreDict
            
    
    '''
    @param scoreDict: dictionary with parsed scores
    Compute scores from input parsed data.
    @return scoreDict: updated dictionary with computed scores
    '''
    def analyse_features(self, scoreDict):
        scoreDict.update(self.lucy_analyze_trees(scoreDict["analysis"], "analysis"))
        scoreDict.update(self.lucy_analyze_trees(scoreDict["generation"], "generation"))
        scoreDict.update(self.lucy_analyze_trees(scoreDict["transfer"], "transfer"))
        return scoreDict
    
    
    '''
    '''
    def lucy_analyze_trees(self, tree_string, prefix):
        #count number of each label
        labels = re.findall(self.treeLabelsCompile, tree_string)
        counts = {}
        for label in labels:
            label.replace("$", "DOLLAR")
            label = "{}_count_{}".format(prefix, label)
            counts[label] = counts.setdefault(label, 0) + 1  
        #convert integers to strings (otherwise writing breaks
        counts = dict([(key, str(value)) for key, value in counts.iteritems()])
        return counts
        

class ApertiumFeatureGenerator():
    '''
    @param inputPath: path to directory with input files
    @param outputFile: path to output file including output filename
    @param langsrc: abbreviation of source language
    @param langtgt: abbreviation of target language
    @param testset: testset name (e.g. "newstest2011" or "20000")
    '''
    def __init__(self, inputPath, outputFile, langsrc, langtgt, testset):
        # Apertium - compilations
        self.reTagCompile = re.compile('(<.*?>)')
        
        parallelSentences = []
        i = 0
        while 1:
            i+=1
            print i
            
            srcLine, refLine, tgtLine, annoLine0, annoLine1 = self.read_line(i, inputPath, testset)
            if not srcLine: break # end loop if no more source sentence
            
            scoreDict = self.process_annotations(annoLine0, annoLine1)
            scoreDict = self.analyse_features(scoreDict)
            
            srcSent, refSent, tgtSent = self.process_sentences(srcLine, refLine, tgtLine, scoreDict)
        
            # parallel sentence attributes
            psAtts =  {"langsrc" : langsrc, "langtgt" : langtgt, "testset" : testset, "id" : str(i)}
            
            ps = ParallelSentence(srcSent, tgtSent, refSent, psAtts)
            parallelSentences.append(ps)
        
        Parallelsentence2Jcml(parallelSentences).write_to_file(outputFile)
        del self.srcFile
        del self.refFile
        del self.tgtFile
        del self.annoFile0
        del self.annoFile1
        

    '''
    Read input files and for each call return 1 line from each file. 
    @param i: number of sentence (line)
    @param inputPath: path to directory where input files are
    @param testset: testset name (e.g. "newstest2011" or "20000")
    @return srcLine: source sentence (line)
    @return refLine: reference sentence (line)
    @return tgtLine: target sentence (line)
    @return annoLine0: 1 line in annotation file 1
    @return annoLine1: 1 line in annotation file 2
    '''
    def read_line(self, i, inputPath, testset):
        if i == 1:
            srcSnts = '%s%s.es' % (inputPath, testset)
            refSnts = '%s%s.ref.en' % (inputPath, testset)
            tgtSnts = '%s%s.s1.en' % (inputPath, testset)
            annotation0 = '%s%s.s1.en.annotation.0' % (inputPath, testset)
            annotation1 = '%s%s.s1.en.annotation.1' % (inputPath, testset)
            
            self.srcFile = open(srcSnts, 'r')
            self.refFile = open(refSnts, 'r')
            self.tgtFile = open(tgtSnts, 'r')
            self.annoFile0 = open(annotation0, 'r')
            self.annoFile1 = open(annotation1, 'r')
            
        # get source sentence
        srcLine = self.srcFile.readline().strip()
        
        # get reference sentence
        if self.refFile:
            refLine = self.refFile.readline().strip()
        else:
            refLine = None
       
        # get target sentence
        tgtLine = self.tgtFile.readline().strip()
       
        # get annotations
        annoLine0 = self.annoFile0.readline().strip()
        annoLine1 = self.annoFile1.readline().strip()
        return srcLine, refLine, tgtLine, annoLine0, annoLine1
        

    '''
    Convert sentences (lines) into SimpleSentence objects. 
    @param srcLine: source sentence (line)
    @param refLine: reference sentence (line)
    @param tgtLine: target sentence (line)
    @param scoreDict: dictionary with parsed scores
    @return srcSent: source sentence as SimpleSentence object
    @return refSent: reference sentence as SimpleSentence object
    @return tgtSent: target sentence with scores as SimpleSentence object
    '''
    def process_sentences(self, srcLine, refLine, tgtLine, scoreDict):
        srcSent = SimpleSentence(srcLine)
        if refLine: refSent = SimpleSentence(refLine)
        else: refSent = None
        tgtSent = [SimpleSentence(tgtLine, scoreDict)]
        return srcSent, refSent, tgtSent
       
        
    '''
    Parse input files.
    @param annoFile0: 1st annotation file
    @param annoFile1: 2nd annotation file
    @return dict of features
    ''' 
    def process_annotations(self, annoLine0, annoLine1):
        scoreDict = {}
        scoreDict["system"] = 's1-Apertium'
        
        scoreDict["alignment"] = annoLine0
        scoreDict["generation"] = annoLine1
        scoreDict["untranslated"] = annoLine1.count("^@")
        scoreDict["unanalyzed"] = annoLine1.count("^*")
        scoreDict["unmorph"] = annoLine1.count("^#")
        scoreDict["multiword"] = annoLine1.count(">#")
        scoreDict["joined"] = annoLine1.count("+")
        
        # count number of occurrences of particular tag
        tagsDict = {}
        for tag in self.reTagCompile.findall(annoLine1):
            if tag in tagsDict: tagsDict[tag] += 1
            else: tagsDict[tag] = 1
        
        # write number of occurrences of particular tag into dictionary 
        for key, value in tagsDict.items():
            scoreDict["count_%s" % key.strip('<>')] = str(value)
        return scoreDict
       
            
    '''
    '''
    def analyse_features(self, scoreDict):
        return scoreDict


#inputPath = '/media/DATA/Arbeit/DFKI/120926_ML4HMT-12/testDataESEN/'
#outputFilePath = '/media/DATA/Arbeit/DFKI/120926_ML4HMT-12/testDataESEN/newstest2011.s1-Apertium_.jcml'
#ApertiumFeatureGenerator(inputPath, outputFilePath, 'es', 'en', 'newstest2011')
#outputFilePath = '/media/DATA/Arbeit/DFKI/120926_ML4HMT-12/testDataESEN/newstest2011.s2-Lucy_.jcml'
#LucyFeatureGenerator(inputPath, outputFilePath, 'es', 'en', 'newstest2011')
#outputFilePath = '/media/DATA/Arbeit/DFKI/120926_ML4HMT-12/testDataESEN/newstest2011.s3-Moses_.jcml'
#MosesFeatureGenerator(inputPath, outputFilePath, 'es', 'en', 'newstest2011')
#outputFilePath = '/media/DATA/Arbeit/DFKI/120926_ML4HMT-12/testDataESEN/newstest2011.s4-Moses2_.jcml'
#Moses2FeatureGenerator(inputPath, outputFilePath, 'es', 'en', 'newstest2011', 'testDataESEN')

inputPath = '/media/DATA/Arbeit/DFKI/120926_ML4HMT-12/tuningDataESEN/'
outputFilePath = '/media/DATA/Arbeit/DFKI/120926_ML4HMT-12/tuningDataESEN/20000.s1-Apertium_.jcml'
ApertiumFeatureGenerator(inputPath, outputFilePath, 'es', 'en', '20000')
outputFilePath = '/media/DATA/Arbeit/DFKI/120926_ML4HMT-12/tuningDataESEN/20000.s2-Lucy_.jcml'
LucyFeatureGenerator(inputPath, outputFilePath, 'es', 'en', '20000')
outputFilePath = '/media/DATA/Arbeit/DFKI/120926_ML4HMT-12/tuningDataESEN/20000.s3-Moses_.jcml'
MosesFeatureGenerator(inputPath, outputFilePath, 'es', 'en', '20000')
outputFilePath = '/media/DATA/Arbeit/DFKI/120926_ML4HMT-12/tuningDataESEN/20000.s4-Moses2_.jcml'
Moses2FeatureGenerator(inputPath, outputFilePath, 'es', 'en', '20000', 'tuningDataESEN')
