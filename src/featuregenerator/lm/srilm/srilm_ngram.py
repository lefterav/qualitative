import xmlrpclib 
#import base64
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer
import sys





class SRILMngramGenerator(LanguageFeatureGenerator):
    '''
    Gets all the words of a sentence through a SRILM language model and counts how many of them are unknown (unigram prob -99) 
    '''
    
    def __init__(self, url, lang="en", lowercase=True, tokenize=True):
        '''
        Define connection with the server
        '''
        self.server = xmlrpclib.Server(url)
        self.lang = lang
        self.lowercase = lowercase
        self.tokenize = tokenize
        
    
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
    
    
    def __prepare_sentence__(self, simplesentence):
        sent_string = simplesentence.get_string().strip()
        if self.lowercase:
            sent_string = sent_string.lower()
        if self.tokenize:
            sent_string = sent_string.replace('%',' %') #TODO: this is an issue
            tokenized_string = PunktWordTokenizer().tokenize(sent_string)
            sent_string = ' '.join(tokenized_string)
        else:
            tokenized_string = sent_string.split(' ')
            
        
        return (tokenized_string, sent_string)
    
    
    def __prepare_sentence_b64__(self, simplesentence):
        sent_string = simplesentence.get_string().strip()
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
        
        return tokenized_string
    
    
    def get_features_simplesentence(self, simplesentence):
        (tokens,sent_string) = self.__prepare_sentence__(simplesentence)
        unk_count = 0
        uni_probs = 1
        bi_probs = 1
        tri_probs = 1
        unk_tokens = []
        
        #check for unknown words and collecting unigram probabilities:
        for token in tokens:
            try: 
                uni_prob = self.server.getUnigramProb(token)
                #uni_prob = self.server.getUnigramProb(base64.standard_b64encode(token))
                if uni_prob == -99:
                    unk_count += 1
                    unk_tokens.append(token)
                    sys.stderr.write("Unknown word: %s\n" % token)
                else:
                    uni_probs += uni_prob
            except: 
                sys.stderr.write("Failed to retrieve unigram probability for token: '%s'\n" % token) 
                pass
        
        
        #get bigram probabilities
        for pos in range ( len(tokens) -1 ):
            token = tokens[pos:pos+2]
            if (token[0] not in unk_tokens) and (token[1] not in unk_tokens):
                try:
                    bi_prob = self.server.getBigramProb(' '.join(token))
                    #bi_prob = self.server.getBigramProb(base64.standard_b64encode(' '.join(token)))
                    bi_probs += bi_prob
                except:
                    sys.stderr.write("Failed to retrieve bigram probability for tokens: '%s'\n" % ' '.join(token)) 

         
        #get trigram probabilities
        for pos in range ( len(tokens) -2 ):
            token = tokens[pos:pos+3]
            if (token[0] not in unk_tokens) and (token[1] not in unk_tokens) and (token[2] not in unk_tokens):
                try:
                    tri_prob = self.server.getTrigramProb(' '.join(token))
                    tri_probs += tri_prob
                except:
                    sys.stderr.write("Failed to retrieve trigram probability for tokens: '%s'\n" % ' '.join(token)) 
        
        attributes = { 'unk' : str(unk_count),
                       'uni-prob' : str(uni_probs),
                       'bi-prob' : str(bi_probs),
                       'tri-prob' : str(tri_probs) }
        
        return attributes
            
            
    
    
    def __get_sentence_probability__(self, sent_string ):
        
        l = len(sent_string.split(" "))       
   
        #print l, sent_string
        return str (self.server.getSentenceProb(sent_string, l))
        
    
    def add_features_batch(self, parallelsentences):
        batch = []
        preprocessed_batch = []
        for parallelsentence in parallelsentences:
            batch.append((parallelsentence.serialize(), parallelsentence.get_attribute("langsrc"),  parallelsentence.get_attribute("langtgt")))
        
        for (row, langsrc, langtgt) in batch:
            preprocessed_row = []
            col_id = 0
            for simplesentence in row:
                if (col_id == 0 and langsrc == self.lang) or (col_id > 0 and langtgt == self.lang):
                    simplesentence = self.__prepare_sentence_b64__(simplesentence)
                    preprocessed_row.append(simplesentence)
                else:
                    simplesentence = ["DUMMY"]
                    preprocessed_row.append(simplesentence)
                col_id += 1
            preprocessed_batch.append(preprocessed_row)
        
        print "sending request"
        features_batch = self.server.getNgramFeatures_batch(preprocessed_batch)
        
        row_id = 0

        
        new_parallelsentences = []
        for row in features_batch:
            parallelsentence = parallelsentences[row_id]
            src = parallelsentence.get_source()
            targets = parallelsentence.get_translations()
            
            column_id = 0
            #dig in the batch to retrieve features
            for feature_set in row:
                for key in feature_set:
                    if column_id == 0:
                        src.add_attribute(key, feature_set[key])
                    else:
                        targets[column_id - 1].add_attribute(key, feature_set[key])
                
                    
                column_id += 1
            
            parallelsentence.set_source(src)
            parallelsentence.set_translations(targets)
            new_parallelsentences.append(parallelsentence)
            row_id += 1
        
        return new_parallelsentences
                
            
        
            
                
                
                