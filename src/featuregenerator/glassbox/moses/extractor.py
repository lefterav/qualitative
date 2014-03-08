'''
Created on Apr 2, 2012

@authors: Lukas Poustka, Eleftherios Avramidis
'''

from optparse import OptionParser
from collections import OrderedDict, defaultdict
import re
import logging
import sys
from numpy import average, var, std, min, max

"""
This class reads Moses verbose output with translation system analysis 
and parses as much information as possible into a flat dictionary.
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
        self.traOpts = re.compile('.* :: pC=([\d.-]+), c=([\d.-]+) c=[\d.-]+ \[\[(\d*)..(\d*)\]\]<<[^>]*>>')
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
        self.timSearch = re.compile('Search took ([\d.-]+) seconds')
        self.timTranslation = re.compile('Translation took ([\d.-]+) seconds')
        self.totSouWor = re.compile('total source words = ([\d.-]+)\n')
        self.worDel = re.compile('words deleted = ([\d.-]+)')
        self.worIns = re.compile('words inserted = ([\d.-]+)')
        self.besTraTot = re.compile('BEST TRANSLATION:.+?[[]total=([\d.-]+)[]]')
        self.besTraTot2 = re.compile('Source and Target Units:.+?[[]total=([\d.-]+)[]]')
        self.besTraVal = re.compile('BEST TRANSLATION:.+?<<(.+?)>>')
        self.besTraVal2 = re.compile('Source and Target Units:.+?<<(.+?)>>')
        self.besTrans = re.compile('BEST TRANSLATION:(.*)\[11')
        self.besTrans2 = re.compile('Source and Target Units:(.*)')
        self.pC = re.compile('[[].+?pC=([\d.-]+).+?[]]')
        self.bestPhrBoundaries = re.compile('\[\[(\d*)\.\.(\d*)\]:([^::]*)')
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
                try:
                    dictOfSntAttrs.append(self.get_sentence_attributes(transPart))
                except ZeroDivisionError:
                    #sys.exit("ZeroDivisionError occurred on line {}\nPlease check the verbose output yourself:\n\n{}".format(lineNo, transPart))
                    logging.warn("Probably no phrases found. Maybe we need to skip this sentence")
                    dictOfSntAttrs.append({})
                    
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
        attrs = OrderedDict()
        # get 'Total translation options'
        attrs['total_transopt'] = self.totTraOpt.search(transPart).group(1)
        
        # get 'Total translation options pruned'
        attrs['total_transopt_pruned'] = self.totTraOptPru.search(transPart).group(1)
        
        # get 'translation options spanning'
        #traOptSpa = self.traOptSpa.findall(transPart)
        #if not traOptSpa: 
        #    logging.warn('translation options spanning not found!\n')
        #else:
        #    for item in traOptSpa:
        #        attrs['transopt_spanning', item[0], item[1]] = item[2]
        
        # get 'future cost'
        #futCos = self.futCos.findall(transPart)
        #if not futCos: 
        #    logging.warn('future cost not found!\n')
        #else:
        #    for item in traOptSpa:
        #        attrs['future_cost', item[0], item[1]] = item[2]
        
        # get 'total hypothesis considered'
        attrs['total_hypotheses'] = self.totHypCon.search(transPart).group(1)
        
        # get 'hypothesis not built'
        attrs['hyp_not_built'] = self.hypNotBui.search(transPart).group(1)
        
        # get 'hypothesis discarded earlier'
        attrs['hyp_disc_earlier'] = self.hypDisEar.search(transPart).group(1)
        
        # get 'hypothesis discarded'
        attrs['hyp_discarded'] = self.hypDis.search(transPart).group(1)
        
        # get 'hypothesis recombined'
        attrs['hyp_recombined'] = self.hypRec.search(transPart).group(1)
        
        # get 'hypothesis pruned'
        attrs['hyp_pruned'] = self.hypPru.search(transPart).group(1)
        
        # get 'time to collect options'
        attrs['time_collect_opt'], attrs['time_per_collect_opt'] = self.timColOpt.search(transPart).group(1,2)
        attrs['time_per_collect_opt'] = float(attrs['time_per_collect_opt'])/100
#        
#        # get 'time to create hypothesis'
        attrs['time_create_hyp'], attrs['time_per_create_hyp'] = self.timCreHyp.search(transPart).group(1,2)
        attrs['time_per_create_hyp'] = float(attrs['time_per_create_hyp'])/100
        
#        # get 'time to estimate score'
        attrs['time_estimate_score'], attrs['time_per_estimate_score'] = self.timEstSco.search(transPart).group(1,2)
        attrs['time_per_estimate_score'] = float(attrs['time_per_estimate_score'])/100
#        
#        # get 'time to calculate lm'
        attrs['time_calculate_lm'], attrs['time_per_calculate_lm'] = self.timCalLm.search(transPart).group(1,2)
        attrs['time_per_calculate_lm'] = float(attrs['time_per_calculate_lm'])/100 
#        
#        # get 'time to other hypothesis score'
        attrs['time_other_hyp_score'], attrs['time_per_other_hyp_score'] = self.timOthHypSco \
                                                  .search(transPart).group(1,2)
        
        attrs['time_per_other_hyp_score'] = float(attrs['time_per_other_hyp_score'])/100
                                                  
#
#        # get 'time to manage stacks'
        attrs['time_manage_stacks'], attrs['time_per_manage_stacks'] = self.timManSta.search(transPart).group(1,2)
        attrs['time_per_manage_stacks'] = float(attrs['time_per_manage_stacks'])/100
#        
#        # get 'time to other'
        attrs['time_other'], attrs['time_per_other'] = self.timOth.search(transPart).group(1,2)
        attrs['time_per_other'] = float(attrs['time_per_other'])/100
        
        attrs['time_search'] =  self.timSearch.search(transPart).group(1)
        
        attrs['time_translation'] =  self.timTranslation.search(transPart).group(1)
        
        # get 'total source words'
        attrs['total_source_words'] = self.totSouWor.search(transPart).group(1)
        
        # get 'words deleted'
        attrs['words_deleted'] = self.worDel.search(transPart).group(1)
        
        # get 'words inserted'
        attrs['words_inserted'] = self.worIns.search(transPart).group(1)
        
        # get 'best translation - total'
        try:
            attrs['best_trans_total'] = self.besTraTot.search(transPart).group(1)
            best_trans_values = re.findall('([\d.-]+)', self.besTraVal \
                                                   .search(transPart).group(1))
            #best trans values is fixed, equal to the number of weights
            for i, trans_value in enumerate(best_trans_values):
                attrs['best_trans_val_{}'.format(i)] = trans_value
        except:
            pass
            #attrs['best_trans_total'] = self.besTraTot2.search(transPart).group(1)
            #best_trans_values = re.findall('([\d.-]+)', self.besTraVal2 \
            #                                       .search(transPart).group(1))
            #best trans values is fixed, equal to the number of weights
            #for i, trans_value in enumerate(best_trans_values):
            #    attrs['best_trans_val_{}'.format(i)] = trans_value

        
        # get 'best translation - values' 
        
#        
#        # get 'pC parameters'
        pC = [float(i) for i in self.pC.findall(transPart)]
        phrases = len(pC)
        attrs['pC_avg'] = average(pC)
        attrs['pC_var'] = var(pC)
        attrs['pC_std'] = std(pC)
        
        if phrases == 0:
            logging.warn("No phrases found. I won't produce any more attributes for this sentence")
            return attrs
        

        attrs['pC_min'] = min(pC)
        attrs['pC_min_pos'] = (1.00*pC.index(attrs['pC_min']))/phrases
        attrs['pC_max'] = max(pC)
        attrs['pC_max_pos'] = (1.00*pC.index(attrs['pC_max']))/phrases
        
            
        pClow = 0
        pChigh = 0
        
        #count the number of the phrases that have too low or too high pC
        for pC_item in pC:
            if pC_item < (attrs['pC_avg'] - attrs['pC_std']):
                pClow += 1
            elif pC_item > (attrs['pC_avg'] + attrs['pC_std']):
                pChigh += 1
        
        attrs["pC_low"] = pClow
        attrs["pC_low_avg"] = 1.00*pClow/phrases
        attrs["pC_high"] = pChigh
        attrs["pC_high_avg"] = 1.00*pChigh/phrases
        
#        # get 'c parameters'
#        attrs['c'] = self.c.findall(transPart)
        c = [float(i) for i in self.c.findall(transPart)]
        attrs['c_avg'] = average(c)
        attrs['c_var'] = var(c)
        attrs['c_std'] = std(c)
        attrs['c_min'] = min(c)
        attrs['c_min_pos'] = (1.00*c.index(attrs['c_min']))/phrases
        attrs['c_max'] = max(c)
        attrs['c_max_pos'] = (1.00*c.index(attrs['c_max']))/phrases
        
        
        #count the number of the phrases that have too low or too high c

        clow = 0
        chigh = 0
        for c_item in c:
            if c_item < (attrs['c_avg'] - attrs['c_std']):
                clow += 1
            elif c_item > (attrs['c_avg'] + attrs['c_std']):
                chigh += 1
                
        attrs["c_low"] = clow
        attrs["c_low_avg"] = 1.00*clow/phrases
        attrs["c_high"] = chigh
        attrs["c_high_avg"] = 1.00*chigh/phrases
        
            
        attrs['phrases'] = phrases
            
        #end if not phrases == 0
        
        try:
            translation_string = self.besTrans.search(transPart).group(1)
        except:
            translation_string = self.besTrans2.search(transPart).group(1)
        token_list = translation_string.strip().split()
        tokens = len(token_list)
        attrs['tgt_tokens'] = tokens
        attrs['tgt_avg_phrase_len'] = (1.00*tokens)/phrases
        
        attrs['unk'] = translation_string.count('|UNK ')
        attrs['unk_per_tokens'] = (1.00*attrs['unk'])/tokens
        unk_pos = [pos for pos,token in enumerate(token_list,1) if token.endswith('|UNK')]
        if not unk_pos:
            unk_pos = [0]
        attrs['unk_pos_first'] = 1.00*min(unk_pos)/tokens
        attrs['unk_pos_last'] = 1.00*max(unk_pos)/tokens
        attrs['unk_pos_avg'] = 1.00*average(unk_pos)/tokens
        attrs['unk_pos_var'] = 1.00*var(unk_pos)
        attrs['unk_pos_std'] = 1.00*std(unk_pos)
        
        #the next line calculates tuples of source-phrase length and target-phrase length, 
        #for each of the decoding phrases
        best_phrase_sizes = [(int(end)-int(start)+1, len(tgt.strip().split())) for start,end,tgt in self.bestPhrBoundaries.findall(transPart)]
        best_src_phrase_sizes = [i[0]for i in best_phrase_sizes]
        src_tgt_diffs = [srclen-tgtlen for srclen,tgtlen in best_phrase_sizes]
        attrs['src_tgt_diff_max'] = max(src_tgt_diffs)
        attrs['src_tgt_diff_min'] = min(src_tgt_diffs)
        attrs['src_tgt_diff_avg'] = average(src_tgt_diffs)
        attrs['src_tgt_diff_std'] = std(src_tgt_diffs)
        attrs['src_phrase_len_avg'] = average(best_src_phrase_sizes)
        attrs['src_phrase_len_var'] = var(best_src_phrase_sizes)
        attrs['src_phrase_len_std'] = std(best_src_phrase_sizes)
        attrs['src_phrase_len_min'] = min(best_src_phrase_sizes)
        attrs['src_phrase_pos_min'] = (1.00*best_src_phrase_sizes.index(attrs['src_phrase_len_min']))/phrases
        attrs['src_phrase_len_max'] = max(best_src_phrase_sizes)
        attrs['src_phrase_pos_max'] = (1.00*best_src_phrase_sizes.index(attrs['src_phrase_len_max']))/phrases
        
        #get all the translation options
        translation_options = self.traOpts.findall(transPart)
        #group the translation options for starting index
        pC_dict = defaultdict(list)
        c_dict = defaultdict(list)
        
        for pC, c, startindex, endindex in translation_options:
            pC_dict[startindex].append(float(pC))
            c_dict[startindex].append(float(c))
        
        #get ambiguity statistics for each translation option per index
        alt_count = []
        alt_pC_avg_all = []
        alt_c_avg_all = []
        alt_pC_std_all = []
        alt_c_std_all = []
        alt_pC_var_all = []
        alt_c_var_all = []
        alt_pC_min_minus_std_all = []
        alt_c_min_minus_std_all = []
        
        clow = 0
        chigh = 0
        pClow = 0
        pChigh = 0
        
        alt_count_all = 0
        
        for startindex in pC_dict.keys():
            alt_pC = pC_dict[startindex]
            alt_c = c_dict[startindex]
            
            alt_count.append(len(alt_pC))
            
            alt_pC_avg = average(alt_pC)
            alt_pC_avg_all.append(alt_pC_avg)
            
            alt_c_avg = average(alt_c)
            alt_c_avg_all.append(alt_c_avg)
                        
            alt_pC_std = std(alt_pC)
            alt_pC_std_all.append(alt_pC_std)
                      
            alt_c_std = std(alt_c)
            alt_c_std_all.append(alt_c_std)
            
            #count the pCs that are lower than the std
            for alt_pC_item in alt_pC:
                alt_count_all +=1

                if alt_pC_item < (alt_pC_avg - alt_pC_std):
                    pClow += 1
                elif alt_pC_item > (alt_pC_avg + alt_pC_std):
                    pChigh += 1
            
            
            
            for alt_c_item in alt_c:
                if alt_c_item < (alt_c_avg - alt_c_std):
                    clow += 1
                elif alt_c_item > (alt_c_avg + alt_c_std):
                    chigh += 1
            
            alt_pC_var = var(alt_pC)
            alt_pC_var_all.append(alt_pC_var)
            
            alt_c_var = var(alt_c)
            alt_c_var_all.append(alt_c_var)
            
            #find how far the best value from the std deviation is
            alt_pC_min_minus_std_all.append(min(alt_pC) - std(alt_pC))
            alt_c_min_minus_std_all.append(min(alt_c) - std(alt_c))
        
        attrs['alt_count_avg'] = average(alt_count)
        attrs['alt_pC_avg_avg'] = average(alt_pC_avg_all)
        attrs['alt_c_avg_avg'] = average(alt_c_avg_all)
        attrs['alt_pC_std_avg'] = average(alt_pC_std_all)
        attrs['alt_c_std_avg'] = average(alt_c_std_all)
        attrs['alt_pC_var_avg'] = average(alt_pC_var_all)
        attrs['alt_c_var_avg'] = average(alt_c_var_all)
        attrs['alt_pC_min_minus_std_all'] = average(alt_pC_min_minus_std_all)
        attrs['alt_c_min_minus_std_all'] = average(alt_c_min_minus_std_all)
        attrs['alt_pC_low'] = pClow
        attrs['alt_pC_high'] = pChigh
        attrs['alt_c_low'] = clow
        attrs['alt_c_high'] = chigh
        if alt_count_all!=0:
            attrs['alt_pC_low_avg'] = 1.00*pClow / alt_count_all
            attrs['alt_pC_high_avg'] = 1.00*pChigh / alt_count_all
            attrs['alt_c_low_avg'] = 1.00*clow / alt_count_all
            attrs['alt_c_high_avg'] = 1.00*pChigh / alt_count_all
        else:
            logging.warn('Zero number of alternative trans')
            attrs['alt_pC_low_avg'] = float("NaN")
            attrs['alt_pC_high_avg'] = float("NaN")
            attrs['alt_c_low_avg'] = float("NaN")
            attrs['alt_c_high_avg'] = float("NaN")
        
        attrsReadable = '\n'.join(['%s = %s' % (str(item), str(value)) for item, value in attrs.items()])
        logging.debug('{}\n'.format(attrsReadable))
        
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
