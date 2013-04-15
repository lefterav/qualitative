'''
Created on Apr 2, 2012

@author: jogin
'''

from optparse import OptionParser
import re
import sys


"""
This class reads txt file with translation system analysis for a few sentences
and parses as much information as possible into a dictionary.
"""
class MosesGlassboxExtractor:
    """
    @param filename: Name of input file with translation system analysis.
    @type filename: string
    """
    def __init__(self):
        
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

        
        #return self.dictOfSntAttrs
        
        
    """
    This function creates per 1 iteration 1 dictionary with parsed sentence attributes. 
    Every dic gets added into a list
    @param filename: Name of input file with translation system analysis.
    @type filename: string 
    @return: a list with one dictionary per sentence
    @rtype: [{feature_name:feature_value, ...}, ...] 
    """       
    def create_dicts_of_sentences_attributes(self, filename):
        dictOfSntAttrs = []
        f = file(filename)
        lineNo = 0
        lines = []
        for line in f:
            lineNo = lineNo + 1
            #print lineNo
            if not line.startswith('Finished translating\n'):
                lines.append(line)
            else: 
                transPart = ''.join(lines)
                dictOfSntAttrs.append(self.get_sentence_attributes(transPart))
                lines = []
                
        f.close()
        return dictOfSntAttrs
    
    """
    This function parses attributes of 1 sentence. 
    @param transPart: translation system analysis for 1 line (1 sentence)
    @type transPart: string
    @return: a dictionary with sentence attributes
    @rtype: {feature_name:feature_value, ...} 
    """
    def get_sentence_attributes(self, transPart):
        attrs = {}
        # get 'Total translation options'
        attrs['total_transl_options'] = self.totTraOpt.search(transPart).group(1)
        
        # get 'Total translation options pruned'
        attrs['total_transl_options_pruned'] = self.totTraOptPru.search(transPart).group(1)
        
        # get 'translation options spanning'
        traOptSpa = self.traOptSpa.findall(transPart)
        if not traOptSpa: 
            sys.stderr.write('translation options spanning not found!\n')
        else:
            for item in traOptSpa:
                attrs['transl_options_spanning', item[0], item[1]] = item[2]
        
        # get 'future cost'
        futCos = self.futCos.findall(transPart)
#        if not futCos: 
#            sys.stderr.write('future cost not found!')
#        else:
#            for item in traOptSpa:
#                attrs['future_cost', item[0], item[1]] = item[2]
        
        # get 'total hypothesis considered'
        attrs['total_hypothesis'] = self.totHypCon.search(transPart).group(1)
        
        # get 'hypothesis not built'
        attrs['hypothesis_not_built'] = self.hypNotBui.search(transPart).group(1)
        
        # get 'hypothesis discarded earlier'
        attrs['hypothesis_disc_earlier'] = self.hypDisEar.search(transPart).group(1)
        
        # get 'hypothesis discarded'
        attrs['hypothesis_discarded'] = self.hypDis.search(transPart).group(1)
        
        # get 'hypothesis recombined'
        attrs['hypothesis_recombined'] = self.hypRec.search(transPart).group(1)
        
        # get 'hypothesis pruned'
        attrs['hypothesis_pruned'] = self.hypPru.search(transPart).group(1)
        
        # get 'time to collect options'
#        attrs['time_collect_opt'] = self.timColOpt.search(transPart).group(1,2)
#        
#        # get 'time to create hypothesis'
#        attrs['time_create_hypothesis'] = self.timCreHyp.search(transPart).group(1,2)
#        
#        # get 'time to estimate score'
#        attrs['time_estimate_score'] = self.timEstSco.search(transPart).group(1,2)
#        
#        # get 'time to calculate lm'
#        attrs['time_calculate_lm'] = self.timCalLm.search(transPart).group(1,2)
#        
#        # get 'time to other hypothesis score'
#        attrs['time_other_hypothesis_score'] = self.timOthHypSco \
#                                                  .search(transPart).group(1,2)
#        
#        # get 'time to manage stacks'
#        attrs['time_manage_stacks'] = self.timManSta.search(transPart).group(1,2)
#        
#        # get 'time to other'
#        attrs['time_other'] = self.timOth.search(transPart).group(1,2)
        
        # get 'total source words'
        attrs['total_source_words'] = self.totSouWor.search(transPart).group(1)
        
        # get 'words deleted'
        attrs['words_deleted'] = self.worDel.search(transPart).group(1)
        
        # get 'words inserted'
        attrs['words_inserted'] = self.worIns.search(transPart).group(1)
        
        # get 'best translation - total'
        attrs['best_trans_total'] = self.besTraTot.search(transPart).group(1)
        
        # get 'best translation - values' 
#        attrs['best_trans_values'] = re.findall('([\d.-]+)', self.besTraVal \
#                                                   .search(transPart).group(1))
#        
#        # get 'pC parameters'
#        attrs['pC'] = self.pC.findall(transPart)
#        
#        # get 'c parameters'
#        attrs['c'] = self.c.findall(transPart)
        
        attrsReadable = '\n'.join(['%s = %s' % (str(item), str(value)) for item, value in attrs.items()])
        print attrsReadable, '\n'
        
        return attrs
        

if __name__ == '__main__':
    # check command line arguments
    parser = OptionParser()
    parser.add_option("-f", '--filename', dest='filename', \
                        help="Name of input file with translation system analysis")
    options, args = parser.parse_args()
    if not options.filename: sys.exit('ERROR: Option --filename is missing!')
    #filename = '/media/DATA/Arbeit/DFKI/120402_sentence_analysis/SERVICE_EXCELLENCE_cust_euDE_4.txt.log'
    extractor = MosesGlassboxExtractor()
    print extractor.create_dicts_of_sentences_attributes(options.filename)