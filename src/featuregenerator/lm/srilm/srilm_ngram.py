import xmlrpclib 
#import base64
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer
import sys
from util.freqcaser import FreqCaser
from numpy import average, std



class SRILMngramGenerator(LanguageFeatureGenerator):
    '''
    Gets all the words of a sentence through a SRILM language model and counts how many of them are unknown (unigram prob -99) 
    '''
    
    def __init__(self, url, lang="en", lowercase=True, tokenize=True, freqcase_file=False):
        '''
        Define connection with the server
        '''
        self.server = xmlrpclib.Server(url)
        self.lang = lang
        self.lowercase = lowercase
        self.tokenize = tokenize
        self.freqcaser = None
        if freqcase_file:
            self.freqcaser = FreqCaser(freqcase_file)
    
    def get_features_src(self, simplesentence, parallelsentence):
        atts = {}
        src_lang = parallelsentence.get_attribute("langsrc")
        if src_lang == self.lang:
            atts = self.get_features_simplesentence(simplesentence)

        return atts

    def get_features_tgt(self, simplesentence, parallelsentence):
        atts = {}
        tgt_lang = parallelsentence.get_attribute("langtgt")
        if tgt_lang == self.lang:
            atts = self.get_features_simplesentence(simplesentence)
        return atts        
    
    
    def _prepare_sentence(self, simplesentence):
        sent_string = simplesentence.get_string().replace('-',' ').strip()
        if self.freqcaser:
            tokenized_string = self.freqcaser.freqcase(sent_string)
        else:
            if self.lowercase:
                sent_string = sent_string.lower()
            if self.tokenize:
                sent_string = sent_string.replace('%',' %') #TODO: this is an issue
                tokenized_string = PunktWordTokenizer().tokenize(sent_string)
                sent_string = ' '.join(tokenized_string)
            else:
                #split and remove empty tokens (due to multiple spaces)
                tokenized_string = [tok.strip() for tok in sent_string.split(' ') if tok.strip()]
            
        
        return (tokenized_string, sent_string)
    
    
    def prepare_sentence(self, simplesentence):
        sent_string = simplesentence.get_string().replace('-',' ').strip()
        if self.freqcaser:
            tokenized_string = self.freqcaser.freqcase(sent_string)
        else:
            if self.lowercase:
                sent_string = sent_string.lower()
            if self.tokenize:
                sent_string = sent_string.replace('%',' %') #TODO: this is an issue
                tokenized_string = PunktWordTokenizer().tokenize(sent_string)
                sent_string = ' '.join(tokenized_string)
            else:
                tokenized_string = sent_string.split(' ')
        
        #for i in range(len(tokenized_string)):
        #    tokenized_string[i] = base64.standard_b64encode(tokenized_string[i])
        
        return unicode(tokenized_string)
    
    def _standouts(self, vector, sign):
        std_value = std(vector)
        avg_value = average(vector)
        standout = 0
        
        for value in vector:
            if value*sign > (avg_value + sign*std_value):
                standout += 1
            
        return standout
    
    def _standout_pos(self, vector, sign):
        std_value = std(vector)
        avg_value = average(vector)
        standout = []
        
        
        for pos, value in enumerate(vector, start=1):
            if value*sign > (avg_value + sign*std_value):
                standout.append(pos)
            
        return standout
                
    
    def get_features_simplesentence(self, simplesentence):
        (tokens,sent_string) = self._prepare_sentence(simplesentence)
        unk_count = 0
        uni_probs = 1
        bi_probs = 1
        tri_probs = 1
        unk_tokens = []
        
        prob = self._get_sentence_probability(sent_string)
        
        #check for unknown words and collecting unigram probabilities:
        pos = 0
        unk_pos = [] #keep the positions of unknown words
        uni_probs_vector = []
        bi_probs_vector = []
        tri_probs_vector = []
        quint_probs_vector = []
        
        for token in tokens:
                pos+=1
#            try: 
                uni_prob = self.server.getUnigramProb(token)
                #uni_prob = self.server.getUnigramProb(base64.standard_b64encode(token))
                if uni_prob == -99:
                    unk_count += 1
                    unk_pos.append(pos)
                    unk_tokens.append(token)
                    sys.stderr.write("Unknown word: %s of len %d\n" % (token, len(token)))
                else:
                    uni_probs_vector.append(uni_prob)
                    uni_probs += uni_prob
#            except: 
                #sys.stderr.write("Failed to retrieve unigram probability for token: '%s'\n" % token) 
#                pass
        
        
        #get bigram probabilities
        for pos in range ( len(tokens) -1 ):
            token = tokens[pos:pos+2]
            if (token[0] not in unk_tokens) and (token[1] not in unk_tokens):
#                try:
                    bi_prob = self.server.getBigramProb(' '.join(token))
                    #bi_prob = self.server.getBigramProb(base64.standard_b64encode(' '.join(token)))
                    bi_probs += bi_prob
                    bi_probs_vector.append(bi_prob)
#                except:
                    #sys.stderr.write("Failed to retrieve bigram probability for tokens: '%s'\n" % ' '.join(token)) 

         
        #get trigram probabilities
        for pos in range ( len(tokens) -2 ):
            token = tokens[pos:pos+3]
            if (token[0] not in unk_tokens) and (token[1] not in unk_tokens) and (token[2] not in unk_tokens):
#                try:
                    tri_prob = self.server.getTrigramProb(' '.join(token))
                    tri_probs += tri_prob
                    tri_probs_vector.append(tri_prob)
                            
#                except:
                    #sys.stderr.write("Failed to retrieve trigram probability for tokens: '%s'\n" % ' '.join(token))
#                    pass 
        unk_rel_pos = (unk_pos * 1.00) / len(tokens)
        
        attributes = { 'lm_unk_pos_abs_avg' : str(average(unk_pos)),
                       'lm_unk_pos_abs_std' : str(std(unk_pos)),
                       'lm_unk_pos_abs_min' : str(min(unk_pos)),
                       'lm_unk_pos_abs_max' : str(max(unk_pos)),
                       'lm_unk_pos_rel_avg' : str(average(unk_rel_pos)),
                       'lm_unk_pos_rel_std' : str(std(unk_rel_pos)),
                       'lm_unk_pos_rel_min' : str(min(unk_rel_pos)),
                       'lm_unk_pos_rel_max' : str(max(unk_rel_pos)),
                       'lm_unk' : str(unk_count),
                       
                       'lm_uni-prob' : str(uni_probs),                    
                       'lm_uni-prob_avg' : str(average(uni_probs_vector)),
                       'lm_uni-prob_std' : str(std(uni_probs_vector)),
                       'lm_uni-prob_low' : self._standouts(uni_probs_vector, -1),
                       #'lm_uni-prob_high' : self._standouts(uni_probs_vector, +1),
                       'lm_uni-prob_low_pos_avg': average(self._standout_pos(uni_probs_vector, -1)),
                       'lm_uni-prob_low_pos_std': std(self._standout_pos(uni_probs_vector, -1)),

                       'lm_bi-prob' : str(bi_probs),
                       'lm_bi-prob_avg' : str(average(bi_probs_vector)),
                       'lm_bi-prob_std' : str(std(bi_probs_vector)),
                       'lm_bi-prob_low' : self._standouts(bi_probs_vector, -1),
                       #'lm_bi-prob_high' : self._standouts(bi_probs_vector, +1),
                       'lm_bi-prob_low_pos_avg': average(self._standout_pos(bi_probs_vector, -1)),
                       'lm_bi-prob_low_pos_std': std(self._standout_pos(bi_probs_vector, -1)),
                       
                       'lm_tri-prob' : str(tri_probs),
                       'lm_tri-prob_avg' : str(average(tri_probs_vector)),
                       'lm_tri-prob_std' : str(std(tri_probs_vector)),
                       'lm_tri-prob_low' : self._standouts(tri_probs_vector, -1),
                       #'lm_tri-prob_high' : self._standouts(tri_probs_vector, +1),
                       'lm_tri-prob_low_pos_avg': average(self._standout_pos(tri_probs_vector, -1)),
                       'lm_tri-prob_low_pos_std': std(self._standout_pos(tri_probs_vector, -1)),
                       'lm_prob' : str(prob) }
        
        return attributes
            
            
    
    
    def _get_sentence_probability(self, sent_string ):
        
        l = len(sent_string.split(" "))       
   
        #print l, sent_string
        return str (self.server.getSentenceProb(sent_string, l))
    

    def xmlrpc_call(self, batch):
        return self.server.getNgramFeatures_batch(batch)
        

    
#    def add_features_batch(self, parallelsentences):
#        
#        #return self.add_features_batch_xmlrpc(parallelsentences)
#        batch = []
#        preprocessed_batch = []
#        for parallelsentence in parallelsentences:
#            batch.append((parallelsentence.serialize(), parallelsentence.get_attribute("langsrc"),  parallelsentence.get_attribute("langtgt")))
#        
#        for (row, langsrc, langtgt) in batch:
#            preprocessed_row = []
#            col_id = 0
#            for simplesentence in row:
#                if (col_id == 0 and langsrc == self.lang) or (col_id > 0 and langtgt == self.lang):
#                    simplesentence = self.prepare_sentence(simplesentence)
#                    preprocessed_row.append(simplesentence)
#                else:
#                    simplesentence = ["DUMMY"]
#                    preprocessed_row.append(simplesentence)
#                col_id += 1
#            preprocessed_batch.append(preprocessed_row)
#        
#        print "sending request"
#        features_batch = self.server.getNgramFeatures_batch(preprocessed_batch)
#        
#        row_id = 0
#
#        
#        new_parallelsentences = []
#        for row in features_batch:
#            parallelsentence = parallelsentences[row_id]
#            src = parallelsentence.get_source()
#            targets = parallelsentence.get_translations()
#            
#            column_id = 0
#            #dig in the batch to retrieve features
#            for feature_set in row:
#                for key in feature_set:
#                    if column_id == 0:
#                        src.add_attribute(key, feature_set[key])
#                    else:
#                        targets[column_id - 1].add_attribute(key, feature_set[key])
#                
#                    
#                column_id += 1
#            
#            parallelsentence.set_source(src)
#            parallelsentence.set_translations(targets)
#            new_parallelsentences.append(parallelsentence)
#            row_id += 1
#        
#        return new_parallelsentences
                
            
        
            
                
                
                