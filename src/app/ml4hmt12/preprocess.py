'''
Created on Sep 26, 2012
@author: jogin

This script converts txt inputs from testDataESEN directory (or tuningDataESEN) into .jcml format.
There are 4 classes - Apertium, Lucy, Moses and HieroMoses.
'''

from dataprocessor.sax.saxps2jcml import Parallelsentence2Jcml
from numpy import average, var, std, array
from optparse import OptionParser
import os
import re
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
import sys


class GlassFeatureGenerator():
    def read_line(self, i, inputFilenames, testset):
        raise NotImplementedError()
    
    def process_annotations(self, annoLines):
        raise NotImplementedError()
    
    def analyse_features(self, i, scoreDict, attrs):
        raise NotImplementedError()
    
    def parse_sentences(self, inputFilenames, outputFile, langsrc, langtgt, testset):
        parallelSentences = []
        i = 0
        while 1:
            i+=1
            print i
            
            srcLine, refLine, tgtLine, annoLines = self.read_line(i, inputFilenames, testset)
            if not srcLine: break # end loop if no more source sentence
            
            scoreDict = self.get_features_tgt(i, annoLines)
            
            #create SimpleSentence objects
            srcSent, refSent, tgtSent = self.process_textfiles(srcLine, refLine, tgtLine, scoreDict)
        
            # parallel sentence attributes
            psAtts =  {"langsrc" : langsrc, "langtgt" : langtgt, "testset" : testset, "id" : str(i)}

            ps = ParallelSentence(srcSent, tgtSent, refSent, psAtts)
            parallelSentences.append(ps)
    
        Parallelsentence2Jcml(parallelSentences).write_to_file(outputFile)
    
    
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
    def process_textfiles(self, srcLine, refLine, tgtLine, scoreDict):
        srcSent = SimpleSentence(srcLine)
        if refLine: refSent = SimpleSentence(refLine)
        else: refSent = None
        tgtSent = [SimpleSentence(tgtLine, scoreDict)]
        return srcSent, refSent, tgtSent
    
    
    '''
    @param i: number of sentence (line)
    @param annoLines: list of lines - always 1 line from 1 annotation file
    @return scoreDict: dict of features
    '''
    def get_features_tgt(self, i, annoLines):
        scoreDict, attrs = self.process_annotations(annoLines)
        scoreDict = self.analyse_features(i, scoreDict, attrs)            
        return scoreDict


class HieroMosesFeatureGenerator(GlassFeatureGenerator):
    '''
    @param inputFilenames: list of input files (src, ref, tgt, annotation)/(src, ref, tgt, annotation0, ..., annotation4)
    @param outputFile: path to output file including output filename
    @param langsrc: abbreviation of source language
    @param langtgt: abbreviation of target language
    @param testset: testset name (e.g. "newstest2011" or "20000")
    @param selectDir: name of directory with input files (either testDataESEN or tuningDataESEN)
    '''
    def __init__(self, inputFilenames, outputFile, langsrc, langtgt, testset):
        # HieroMoses - compilations
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
        self.iFile = 0
        self.nextString = ''
        
        self.parse_sentences(inputFilenames, outputFile, langsrc, langtgt, testset)


    '''
    Read input files and for each call return 1 line from each file. 
    @param i: number of sentence (line)
    @param inputPath: path to directory where input files are
    @param testset: testset name (e.g. "newstest2011" or "20000")
    @return srcLine: source sentence (line)
    @return refLine: reference sentence (line)
    @return tgtLine: target sentence (line)
    @return annoLines: list of lines - always 1 line from 1 annotation file
    '''
    def read_line(self, i, inputFilenames, testset):
        if i == 1:
            srcSnts = inputFilenames[0]
            refSnts = inputFilenames[1]
            tgtSnts = inputFilenames[2]
            
            if len(inputFilenames) == 4: # if testDataESEN
                annotation = inputFilenames[3]
            elif len(inputFilenames) == 8: # if tuningDataESEN
                annotation0 = inputFilenames[3]
                annotation1 = inputFilenames[4]
                annotation2 = inputFilenames[5]
                annotation3 = inputFilenames[6]
                annotation4 = inputFilenames[7]
            else:
                sys.exit('Too many or too little filenames.')
            
            self.srcFile = open(srcSnts, 'r')
            self.refFile = open(refSnts, 'r')
            self.tgtFile = open(tgtSnts, 'r')
            if len(inputFilenames) == 4: # if testDataESEN
                self.annoFile0 = open(annotation, 'r') # testDataESEN
                self.annoFile1 = None # empty
                self.annoFile2 = None # empty
                self.annoFile3 = None # empty
                self.annoFile4 = None # empty
            if len(inputFilenames) == 8: # if tuningDataESEN
                self.annoFile0 = open(annotation0, 'r') # tuningDataESEN
                self.annoFile1 = open(annotation1, 'r') # tuningDataESEN
                self.annoFile2 = open(annotation2, 'r') # tuningDataESEN
                self.annoFile3 = open(annotation3, 'r') # tuningDataESEN
                self.annoFile4 = open(annotation4, 'r') # tuningDataESEN
        
        # get source sentence
        srcLine = self.srcFile.readline().strip()
        if not srcLine: return None, None, None, None
        
        # get reference sentence
        if self.refFile:
            refLine = self.refFile.readline().strip()
        else:
            refLine = None
       
        # get target sentence
        tgtLine = self.tgtFile.readline().strip()
       
        # get annotations
        if len(inputFilenames) == 8: # if tuningDataESEN
            annoFiles = [self.annoFile0, self.annoFile1, self.annoFile2, self.annoFile3, self.annoFile4]
        annoLine = self.nextString
        while 1:
            # if testDataESEN
            if len(inputFilenames) == 4: line = self.annoFile0.readline().strip()
            # if tuningDataESEN
            if len(inputFilenames) == 8: line = annoFiles[self.iFile].readline().strip()            
            if line and not line.count('Trans Opt %s' % (i%4000)):
                annoLine += line
            elif not line: # detect end of file
                self.iFile += 1
                self.nextString = ''
                break
            else: # detect end of sentence
                self.nextString = line
                break
        annoLines = [annoLine]
        return srcLine, refLine, tgtLine, annoLines
    
    
    '''
    Parse input files.
    @param annoLines: list of lines - always 1 line from 1 annotation file
    @return scoreDict: dict of features
    @return attrs: list of parsed attributes
    ''' 
    def process_annotations(self, annoLines):
        annoLine = annoLines[0]
        scoreDict = {}
        scoreDict["system"] = 's4-HieroMoses'

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
    Compute scores from input parsed data.
    @param i: number of sentence (line)
    @param scoreDict: dictionary with parsed scores
    @param attrs: list of parsed attributes
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

        
class MosesFeatureGenerator(GlassFeatureGenerator):
    '''
    @param inputFilenames: list of input files (src, ref, tgt, annotation)
    @param outputFile: path to output file including output filename
    @param langsrc: abbreviation of source language
    @param langtgt: abbreviation of target language
    @param testset: testset name (e.g. "newstest2011" or "20000")
    '''
    def __init__(self, inputFilenames, outputFile, langsrc, langtgt, testset):
        # Moses - compilations
        self.paramsCompile = re.compile('(\d+)..(\d+)](.*?)TRANSLATED AS:(.*?)WORD ALIGNED:(.*?)')
        self.reScoresCompile = re.compile('d: (-*\d+.\d+) w: (-*\d+.\d+) u: (-*\d+.\d+) d: (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) lm: (-*\d+.\d+) tm: (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+) (-*\d+.\d+)')

        self.parse_sentences(inputFilenames, outputFile, langsrc, langtgt, testset)


    '''
    Read input files and for each call return 1 line from each file. 
    @param i: number of sentence (line)
    @param inputFilenames: list of input files (src, ref, tgt, annotation)
    @param testset: testset name (e.g. "newstest2011" or "20000")
    @return srcLine: source sentence (line)
    @return refLine: reference sentence (line)
    @return tgtLine: target sentence (line)
    @return annoLines: list of lines - always 1 line from 1 annotation file
    '''
    def read_line(self, i, inputFilenames, testset):
        if i == 1:
            srcSnts = inputFilenames[0]
            refSnts = inputFilenames[1]
            tgtSnts = inputFilenames[2]
            annotation = inputFilenames[3]
            
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
        annoLines = [annoLine]
        return srcLine, refLine, tgtLine, annoLines
    
    
    '''
    Parse input files.
    @param annoLines: list of lines - always 1 line from 1 annotation file
    @return scoreDict: dict of features
    @return attrs: list of parsed attributes
    ''' 
    def process_annotations(self, annoLines):
        annoLine = annoLines[0]
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
        attrs = []
        return scoreDict, attrs
       
        
    '''    
    Compute scores from input parsed data.
    @param i: number of sentence (line)
    @param scoreDict: dictionary with parsed scores
    @param attrs: list of parsed attributes
    @return scoreDict: updated dictionary with computed scores
    '''    
    def analyse_features(self, i, scoreDict, attrs):
        return scoreDict


class LucyFeatureGenerator(GlassFeatureGenerator):
    '''
    @param inputFilenames: list of input files (src, ref, tgt, annotation0, annotation1)
    @param outputFile: path to output file including output filename
    @param langsrc: abbreviation of source language
    @param langtgt: abbreviation of target language
    @param testset: testset name (e.g. "newstest2011" or "20000")
    '''
    def __init__(self, inputFilenames, outputFile, langsrc, langtgt, testset):
        # Lucy - compilations
        self.unkWordsNoCompile = re.compile('<U\[.*?\]>')
        self.ambiguitiesNoCompile = re.compile('<A\[.*?\]>')
        self.analysisCompile = re.compile('<analysis>(.*?)</analysis>')
        self.transferCompile = re.compile('<transfer>(.*?)</transfer>')
        self.mirCompile = re.compile('<mir>(.*?)</mir>')
        self.generationCompile = re.compile('<generation>(.*?)</generation>')
        self.treeLabelsCompile = re.compile("CAT\s*([^ )]*)")
        
        self.parse_sentences(inputFilenames, outputFile, langsrc, langtgt, testset)


    '''
    Read input files and for each call return 1 line from each file. 
    @param i: number of sentence (line)
    @param inputFilenames: list of input files (src, ref, tgt, annotation0, annotation1)
    @param testset: testset name (e.g. "newstest2011" or "20000")
    @return srcLine: source sentence (line)
    @return refLine: reference sentence (line)
    @return tgtLine: target sentence (line)
    @return annoLines: list of lines - always 1 line from 1 annotation file
    '''
    def read_line(self, i, inputFilenames, testset):
        if i == 1:
            srcSnts = inputFilenames[0]
            refSnts = inputFilenames[1]
            tgtSnts = inputFilenames[2]
            annotation0 = inputFilenames[3]
            annotation1 = inputFilenames[4]
            
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

        annoLines = [annoLine0, annoLine1]
        return srcLine, refLine, tgtLine, annoLines
    

    '''
    Parse input files.
    @param annoLines: list of lines - always 1 line from 1 annotation file
    @return scoreDict: dict of features
    @return attrs: list of parsed attributes
    '''
    def process_annotations(self, annoLines):
        annoLine0 = annoLines[0]
        annoLine1 = annoLines[1]
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
        attrs = []
        return scoreDict, attrs
            
    
    '''    
    Compute scores from input parsed data.
    @param i: number of sentence (line)
    @param scoreDict: dictionary with parsed scores
    @param attrs: list of parsed attributes
    @return scoreDict: updated dictionary with computed scores
    '''
    def analyse_features(self, i, scoreDict, attrs):
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
        

class ApertiumFeatureGenerator(GlassFeatureGenerator):
    '''
    @param inputFilenames: list of input files (src, ref, tgt, annotation0, annotation1)
    @param outputFile: path to output file including output filename
    @param langsrc: abbreviation of source language
    @param langtgt: abbreviation of target language
    @param testset: testset name (e.g. "newstest2011" or "20000")
    '''
    def __init__(self, inputFilenames, outputFile, langsrc, langtgt, testset):
        # Apertium - compilations
        self.reTagCompile = re.compile('(<.*?>)')
        
        self.parse_sentences(inputFilenames, outputFile, langsrc, langtgt, testset)
        

    '''
    Read input files and for each call return 1 line from each file. 
    @param i: number of sentence (line)
    @param inputPath: path to directory where input files are
    @param testset: testset name (e.g. "newstest2011" or "20000")
    @param inputFilenames: list of input files (src, ref, tgt, annotation0, annotation1)
    @return srcLine: source sentence (line)
    @return refLine: reference sentence (line)
    @return tgtLine: target sentence (line)
    @return annoLines: list of lines - always 1 line from 1 annotation file
    '''
    def read_line(self, i, inputFilenames, testset):
        if i == 1:
            srcSnts = inputFilenames[0]
            refSnts = inputFilenames[1]
            tgtSnts = inputFilenames[2]
            annotation0 = inputFilenames[3]
            annotation1 = inputFilenames[4]
            
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
        
        annoLines = [annoLine0, annoLine1]
        return srcLine, refLine, tgtLine, annoLines
       
        
    '''
    Parse input files.
    @param annoLines: list of lines - always 1 line from 1 annotation file
    @return scoreDict: dict of features
    @return attrs: list of parsed attributes
    '''
    def process_annotations(self, annoLines):
        annoLine0 = annoLines[0]
        annoLine1 = annoLines[1]
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
        attrs = []
        return scoreDict, attrs
       
            
    '''    
    Compute scores from input parsed data.
    @param i: number of sentence (line)
    @param scoreDict: dictionary with parsed scores
    @param attrs: list of parsed attributes
    @return scoreDict: updated dictionary with computed scores
    '''
    def analyse_features(self, i, scoreDict, attrs):
        return scoreDict
    

'''
Example for command line:
--system Apertium (implemented: Apertium, Lucy, Moses, HieroMoses)
--srcFile data/newstest2011.es
--refFile data/newstest2011.ref.en
--tgtFile data/newstest2011.s1.en
--outputFile data/results.txt
--srcLang es
--tgtLang en
--testset newstest2011
--annoFiles data/newstest2011.s1.en.annotation.0;data/newstest2011.s1.en.annotation.1
'''

if __name__ == '__main__':

    # command line arguments definition
    parser = OptionParser()
    parser.add_option("-m", '--system', dest='system', \
    help="name of translation system")
    parser.add_option("-s", '--srcFile', dest='srcFile', \
    help="source language file with sentences line-by-line")
    parser.add_option("-r", '--refFile', dest='refFile', \
    help="reference language file with sentences line-by-line")
    parser.add_option("-t", '--tgtFile', dest='tgtFile', \
    help="target language file with sentences line-by-line")
    parser.add_option("-o", '--outputFile', dest='outputFile', \
    help="output file with parsed and eventually analysed scores")
    parser.add_option("-a", '--srcLang', dest='srcLang', \
    help="source language")
    parser.add_option("-b", '--tgtLang', dest='tgtLang', \
    help="target language")
    parser.add_option("-e", '--testset', dest='testset', \
    help="name of testset")
    parser.add_option("-v", '--annoFiles', dest='annoFiles', \
    help="annotation files, multiple files are separated by comma")
    
    # command line arguments check
    opt, args  = parser.parse_args()
    if not opt.system: sys.exit('ERROR: Option --system is missing!')
    if not opt.srcFile: sys.exit('ERROR: Option --srcFile is missing!')
    if not opt.refFile: sys.exit('ERROR: Option --refFiles is missing!')
    if not opt.tgtFile: sys.exit('ERROR: Option --tgtFiles is missing!')
    if not opt.outputFile: sys.exit('ERROR: Option --outputFile is missing!')
    if not opt.srcLang: sys.exit('ERROR: Option --srcLang is missing!')
    if not opt.tgtLang: sys.exit('ERROR: Option --tgtLang is missing!')
    if not opt.testset: sys.exit('ERROR: Option --testset is missing!')
    if not opt.annoFiles: sys.exit('ERROR: Option --annoFiles is missing!')

    if opt.system == 'Apertium':
        inputFilenames = [opt.srcFile, opt.refFile, opt.tgtFile]
        inputFilenames.extend(opt.annoFiles.split(','))
        if len(inputFilenames) < 5: sys.exit('Too little annotation files for Apertium system - 2 needed.')
        if len(inputFilenames) > 5: sys.exit('Too many annotation files for Apertium system - 2 needed.')
        ApertiumFeatureGenerator(inputFilenames, opt.outputFile, opt.srcLang, opt.tgtLang, opt.testset)
    elif opt.system == 'Lucy':
        inputFilenames = [opt.srcFile, opt.refFile, opt.tgtFile]
        inputFilenames.extend(opt.annoFiles.split(','))
        if len(inputFilenames) < 5: sys.exit('Too little annotation files for Lucy system - 2 needed.')
        if len(inputFilenames) > 5: sys.exit('Too many annotation files for Lucy system - 2 needed.')
        LucyFeatureGenerator(inputFilenames, opt.outputFile, opt.srcLang, opt.tgtLang, opt.testset)
    elif opt.system == 'Moses':
        inputFilenames = [opt.srcFile, opt.refFile, opt.tgtFile]
        inputFilenames.extend(opt.annoFiles.split(','))
        if len(inputFilenames) < 4: sys.exit('Too little annotation files for Moses system - 1 needed.')
        if len(inputFilenames) > 4: sys.exit('Too many annotation files for Moses system - 1 needed.')
        MosesFeatureGenerator(inputFilenames, opt.outputFile, opt.srcLang, opt.tgtLang, opt.testset)
    elif opt.system == 'HieroMoses':
        inputFilenames = [opt.srcFile, opt.refFile, opt.tgtFile]
        inputFilenames.extend(opt.annoFiles.split(','))
        if not len(inputFilenames) == 4 and not len(inputFilenames) == 8:
            sys.exit('Too little or too many annotation files for HieroMoses system - 1 or 5 needed.')
        HieroMosesFeatureGenerator(inputFilenames, opt.outputFile, opt.srcLang, opt.tgtLang, opt.testset)
    else:
        sys.exit('System name not implemented. Available: Apertium, Lucy, Moses, HieroMoses')
