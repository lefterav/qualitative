'''
Created on Apr 2, 2012

@author: jogin
'''

from optparse import OptionParser
import re
import sys
import time


"""
This class reads txt file with translation system analysis and saves as
much information as possible to a dictionary.
"""
class ExtractEvaluation:
    """
    @param filename: Name of input file with translation system analysis.
    @type filename: string 
    """
    def __init__(self, filename):
        #start = time.time()
        self.att = {}
        self.parsingTime = 0
        self.totTraOpt = re.compile('Total translation options: ([\d.-]+)\n')
        self.totTraOptPru = re.compile('Total translation options pruned: ([\d.-]+)\n')
        self.traOptSpa = re.compile('translation options spanning from  ([\d.-]+) to ([\d.-]+) is ([\d.-]+)')
        self.futCos = re.compile('future cost from ([\d.-]+) to ([\d.-]+) is ([\d.-]+)\n')
        self.totHypCon = re.compile('total hypotheses considered = ([\d.-]+)\n')
        self.hypNotBui = re.compile('number not built = ([\d.-]+)\n')
        self.hypDisEar = re.compile('number discarded early = ([\d.-]+)\n')
        self.hypDis = re.compile('number discarded = ([\d.-]+)\n')
        self.hypRec = re.compile('number recombined = ([\d.-]+)\n')
        self.hypPru = re.compile('number pruned = ([\d.-]+)\n')
        self.timColOpt = re.compile('time to collect opts    ([\d.-]+) [(]([\d.-]+)%[)]\n')
        self.timCreHyp = re.compile('create hyps     ([\d.-]+) [(]([\d.-]+)%[)]\n')
        self.timEstSco = re.compile('estimate score  ([\d.-]+) [(]([\d.-]+)%[)]\n')
        self.timCalLm = re.compile('calc lm         ([\d.-]+) [(]([\d.-]+)%[)]\n')
        self.timOthHypSco = re.compile('other hyp score ([\d.-]+) [(]([\d.-]+)%[)]\n')
        self.timManSta = re.compile('manage stacks   ([\d.-]+) [(]([\d.-]+)%[)]\n')
        self.timOth = re.compile('other           ([\d.-]+) [(]([\d.-]+)%[)]\n')
        self.totSouWor = re.compile('total source words = ([\d.-]+)\n')
        self.worDel = re.compile('words deleted = ([\d.-]+)')
        self.worIns = re.compile('words inserted = ([\d.-]+)')
        self.besTraTot = re.compile('BEST TRANSLATION:.+?[[]total=([\d.-]+)[]]')
        self.besTraVal = re.compile('BEST TRANSLATION:.+?<<(.+?)>>')
        self.pC = re.compile('[[].+?pC=([\d.-]+).+?[]]')
        self.c = re.compile('[[].+?c=([\d.-]+)[]]')

        f = file(filename)
        lineNo = 0
        partNo = 0
        lines = []
        for line in f:
            lineNo = lineNo + 1
            print lineNo
            if not line.startswith('Finished translating\n'):
                lines.append(line)
            else: 
                transPart = ''.join(lines)
                partNo += 1
                self.add_attributes(transPart, partNo)
                lines = []
                #time.sleep(4)
                
        f.close()
        attrsReadable = '\n'.join(['%s = %s' % (str(item), str(value)) for item, value in self.att.items()])
        f = file('%s_dict' % filename, 'w')
        f.write(attrsReadable)
        f.close()
        #print attrsReadable
        #print time.time()-start
        #print self.parsingTime
        #sys.exit()
                    

    
    """
    This function adds attributes to global dictionary. These attributes are
    parsed from 1 line of translation system analysis. 
    @param transPart: translation system analysis for 1 line (1 sentence)
    @type transPart: string
    @param partNo: number of translation system part
    @type partNo: int 
    """
    def add_attributes(self, transPart, partNo):
        #begin = time.time()
        # get 'Total translation options'
        self.att['total_transl_options', partNo] = self.totTraOpt.search(transPart).group(1)
        
        # get 'Total translation options pruned'
        self.att['total_transl_options_pruned', partNo] = self.totTraOptPru.search(transPart).group(1)
        
        # get 'translation options spanning'
        traOptSpa = self.traOptSpa.findall(transPart)
        if not traOptSpa: sys.exit('translation options spanning not found in part %s!' % partNo)
        for item in traOptSpa:
            self.att['transl_options_spanning', partNo, item[0], item[1]] = item[2]
        
        # get 'future cost'
        futCos = self.futCos.findall(transPart)
        if not futCos: sys.exit('future cost not found in part %s!' % partNo)
        for item in futCos:
            self.att['future_cost', 'snt_%s' % partNo, item[0], item[1]] = item[2]
        
        # get 'total hypothesis considered'
        self.att['total_hypothesis', 'snt_%s' % partNo] = self.totHypCon.search(transPart).group(1)
        
        # get 'hypothesis not built'
        self.att['hypothesis_not_built', 'snt_%s' % partNo] = self.hypNotBui.search(transPart).group(1)
        
        # get 'hypothesis discarded earlier'
        self.att['hypothesis_disc_earlier', 'snt_%s' % partNo] = self.hypDisEar.search(transPart).group(1)
        
        # get 'hypothesis discarded'
        self.att['hypothesis_discarded', 'snt_%s' % partNo] = self.hypDis.search(transPart).group(1)
        
        # get 'hypothesis recombined'
        self.att['hypothesis_recombined', 'snt_%s' % partNo] = self.hypRec.search(transPart).group(1)
        
        # get 'hypothesis pruned'
        self.att['hypothesis_pruned', 'snt_%s' % partNo] = self.hypPru.search(transPart).group(1)
        
        # get 'time to collect options'
        self.att['time_collect_opt', 'snt_%s' % partNo] = self.timColOpt.search(transPart).group(1,2)
        
        # get 'time to create hypothesis'
        self.att['time_create_hypothesis', 'snt_%s' % partNo] = self.timCreHyp.search(transPart).group(1,2)
        
        # get 'time to estimate score'
        self.att['time_estimate_score', 'snt_%s' % partNo] = self.timEstSco.search(transPart).group(1,2)
        
        # get 'time to calculate lm'
        self.att['time_calculate_lm', 'snt_%s' % partNo] = self.timCalLm.search(transPart).group(1,2)
        
        # get 'time to other hypothesis score'
        self.att['time_other_hypothesis_score', 'snt_%s' % partNo] = self.timOthHypSco.search(transPart).group(1,2)
        
        # get 'time to manage stacks'
        self.att['time_manage_stacks', 'snt_%s' % partNo] = self.timManSta.search(transPart).group(1,2)
        
        # get 'time to other'
        self.att['time_other', 'snt_%s' % partNo] = self.timOth.search(transPart).group(1,2)
        
        # get 'total source words'
        self.att['total_source_words', 'snt_%s' % partNo] = self.totSouWor.search(transPart).group(1)
        
        # get 'words deleted'
        self.att['words_deleted', 'snt_%s' % partNo] = self.worDel.search(transPart).group(1)
        
        # get 'words inserted'
        self.att['words_inserted', 'snt_%s' % partNo] = self.worIns.search(transPart).group(1)
        
        # get 'best translation - total'
        self.att['best_trans_total', 'snt_%s' % partNo] = self.besTraTot.search(transPart).group(1)
        
        # get 'best translation - values' 
        self.att['best_trans_values', 'snt_%s' % partNo] = re.findall \
                       ('([\d.-]+)', self.besTraVal.search(transPart).group(1))
        
        # get 'pC parameters'
        self.att['pC', 'snt_%s' % partNo] = self.pC.findall(transPart)
        #print self.pC.findall(transPart)
        
        # get 'c parameters'
        self.att['c', 'snt_%s' % partNo] = self.c.findall(transPart)
        #print self.c.findall(transPart)
        
        #print '\n'.join(['%s = %s' % (str(item), str(value)) for item, value in self.att.items()])
        #if partNo == 1: sys.exit()
        #sys.exit()
        #self.parsingTime += time.time() - begin


# check command line arguments
parser = OptionParser()
parser.add_option("-f", '--filename', dest='filename', \
                    help="Name of input file with translation system analysis")
options, args = parser.parse_args()
if not options.filename: sys.exit('ERROR: Option --filename is missing!')
#filename = '/media/DATA/Arbeit/DFKI/120402_sentence_analysis/SERVICE_EXCELLENCE_cust_euDE_4.txt.log'
ExtractEvaluation(options.filename)