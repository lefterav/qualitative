#!/usr/bin/env python
# -*- coding: utf8 -*-

# Copyright 2011 Maja Popović, 
# Modified 2013 Eleftherios Avramidis
# The program is distributed under the terms 
# of the GNU General Public Licence (GPL)

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Publications of results obtained through the use of original or
# modified versions of the software have to cite the authors by refering
# to the following publication:

# Maja Popović: "Hjerson: An Open Source Tool for Automatic Error
# Classification of Machine Translation Output". The Prague Bulletin of
# Mathematical Linguistics No. 96, pp. 59--68, October 2011
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
from featuregenerator.preprocessor import Tokenizer
from util.treetaggerwrapper import TreeTagger
import logging
import os
sent = False

TAGDIR = "~/taraxu_tools/treetager/"


class Hjerson(LanguageFeatureGenerator):
    """
    This is a class that wraps the Hjerson functionality on a sentence level.
    """
    def __init__(self, **kwargs):
        """
        By initializing Hjerson, we maintain a tokenizer (if needed) and a treetager object
        so that they are available for sentence-level calls
        @keyword tokenize: specify if tokenizer should be run by Hjerson, false if it has already happened
        @type tokenize: boolean
        @keyword lang: specify which language is the content using the language 2-letter iso code
        @type lang: str
        @keyword tagdir: specify the directory where the treetager bin folder exists
        @type tagdir: str 
        """
        self.tokenize = kwargs.setdefault('tokenize', True)
        self.lang = kwargs.setdefault('lang', 'en')
        tagdir = kwargs.setdefault('tagdir', os.path.expanduser(TAGDIR))
        
        if self.tokenize:
            self.tokenizer = Tokenizer(self.lang)
        
        self.treetager = TreeTagger(TAGLANG=self.lang, 
                                    TAGDIR=tagdir, 
#                                    TAGINENC='latin1', 
#                                    TAGOUTENC='latin1'
                                    )
        
        self.totalHypLength = 0.0
        self.totalWerRefLength = 0.0
        
        self.totalWerCount = 0.0
        self.totalRperCount = 0.0
        self.totalHperCount = 0.0
        
        self.totalInflRperCount = 0.0
        self.totalInflHperCount = 0.0
        self.totalMissCount = 0.0
        self.totalExtCount = 0.0
        self.totalRefLexCount = 0.0
        self.totalHypLexCount = 0.0
        self.totalRefReordCount = 0.0
        self.totalHypReordCount = 0.0
        
        self.totalBlockInflRperCount = 0.0
        self.totalBlockInflHperCount = 0.0
        self.totalBlockMissCount = 0.0
        self.totalBlockExtCount = 0.0
        self.totalRefBlockLexCount = 0.0
        self.totalHypBlockLexCount = 0.0
        self.totalRefBlockReordCount = 0.0
        self.totalHypBlockReordCount = 0.0
    
    
    def get_features_tgt(self, simplesentence, parallelsentence):        
        """
        Override language feature generator function in order to return sentence level error classes
        @param simplesentence: a simple sentence object, containing the target sentence
        @type L{sentence.sentence.SimpleSentence}
        @param parallelsentence: a parallel sentence object which is needed to derive the reference
        @type L{sentence.parallelsentence.ParallelSentence}
        @return: a dictionary with the attributes retrieved
        @rtype: {str: object, ... } 
        """
        target_string = simplesentence.get_string()
        ref_string = parallelsentence.ref.get_string()
         
        atts = self.get_features_strings(target_string, [ref_string])
        atts = dict([("ref-hj_{}".format(key), value) for key, value in atts.iteritems()])
        return atts
    
    
    def _tag(self, string):
        strings_tagged = self.treetager.TagText(string, encoding='utf-8')
        tokens = []
        tags = []
        bases = []
        for string_tagged in strings_tagged:
            #try net to catch failed tagging
            try:
                token, tag, base = string_tagged.split("\t")
            except ValueError:
                try:
                    token, tag = string_tagged.split("\t")
                    base = token
                except ValueError:
                    token = string_tagged
                    base = token
                    tag = "NaN"
            tokens.append(token)
            tags.append(tag)
            bases.append(base)
        
        results = (" ".join(tokens), " ".join(tags), " ".join(bases))
        if (len(results[0].split())!=len(results[1].split()) or len(results[1].split())!=len(results[2].split()) or len(results[0].split())!=len(results[2].split())):
            logging.debug("{}".format(results))
        return results
    
    def get_features_strings(self, target_string, references):
        """
        Process one sentence, given the translated sentence (hypothesis) and the corresponding reference
        @param target_string: the translation hypothesis produced by the system
        @type target_string: str
        @param references: a list of strings, containing the correct translations
        @type references: list(str)
        """
                
        if self.tokenize:
            target_string = self.tokenizer.process_string(target_string)
            references = [self.tokenizer.process_string(reference) for reference in references]
        
        #replace target string with the one from the tagger, and also get tags and base forms
        target_string, target_tag, target_base = self._tag(target_string)
        
        #separate references list into two lists, one for tags and one for base forms
        reference_tuples = [self._tag(reference) for reference in references]
        reference_strings = [r[0] for r in reference_tuples]
        reference_tags = [r[1] for r in reference_tuples]
        reference_bases = [r[2] for r in reference_tuples]
        
        return self.analyze(target_string, target_base, target_tag, reference_strings, reference_bases, reference_tags)
    
    
    def analyze(self, hline, basehline, addhline, refs, baserefs, addrefs):
        """
        This functions hosts the core sentence-level functionality of Hjerson, as written originally
        by Maja Popovic. It operates after all sentence-level strings have been retrieved and passed as 
        parameters
        @param hline:
        
        """
          
        p = (0,0)

        Q = {}
        Q[p] = 0
        
        B = {}
        B[p] = levNode(0, 0, 0)
        

        minSentWer = 1000
        bestWerRefLength = 0.0
        bestWerRefIndex = -1
        bestWerRefErrors = []
        bestWerHypErrors = []
        bestWerRefWords = []
        bestWerHypWords = []
        bestWerRefAdd = []
        bestWerHypAdd = []
    
    
        bestSentWer = 0.0
    
        maxLength = []
        
        hypWords = hline.split()
        addhypWords = addhline.split()
        if len(addhypWords) < hypWords:
            addhypWords = [""] * len(hypWords)
        baseHypWords = basehline.split()
    
        self.totalHypLength += len(hypWords)
    
    
        # adjusting hypothesis indices to range from 1 to len(hypWords) (for WER calculation)
    
        hyp = {}
        addhyp = {}
    
        adjust_indices(hypWords, hyp, addhypWords, addhyp)
        
    
        # reading reference(s)
    
        nref = 0
        
        for reference in refs:
            ir = refs.index(reference)
            refWords = reference.split()
            addrefWords = addrefs[ir].split()
            if len(addrefWords) < len(refWords):
                addrefWords = [""] * len(refWords)
            baseRefWords = baserefs[ir].split()
    
    
            # adjusting reference indices to range from 1 to len(refWords) (for WER calculation)
    
            ref = {}
            addref = {}
    
            adjust_indices(refWords, ref, addrefWords, addref)
    
               
            # maximal length (necessary for wer-alignment)
    
            if len(refWords) > len(hypWords):
                maxLength.append(len(refWords))
            else:
                maxLength.append(len(hypWords))
    
    
    
            # WER errors
    
            for nh in range(0, len(hyp)+1):
                p = (0, nh)
                Q[p] = nh
                B[p] = levNode(0, nh-1, 3)
    
                
            for nr in range(0, len(ref)+1):
                p = (nr, 0)
                Q[p] = nr
                B[p] = levNode(nr-1, 0, 2)
                
    
            p = (0, 0)
            B[p] = levNode(-1, -1, -1)
            
            p = (1, 0)
            B[p] = levNode(0, 0, 2)
            
            p = (0, 1)
            B[p] = levNode(0, 0, 3)
    
    
            # Qs and Bs
    
            for r in ref.keys():
                for h in hyp.keys():
                    minQ = 1000
                    p = (r, h)
                    dp = (r-1, h)
                    ip = (r, h-1)
                    sp = (r-1, h-1)
    
    
                    s = 0
                    if hyp[h] != ref[r]:
                        s = 1
                    else:
                        s = 0
                    
                    if Q[sp]+s < minQ:
                        minQ = Q[sp]+s
                        B[p] = levNode(r-1, h-1, s)
            
                    if Q[dp]+1 < minQ:
                        minQ = Q[dp]+1
                        B[p] = levNode(r-1, h, 2)
    
                    if Q[ip]+1 < minQ:
                        minQ = Q[ip]+1
                        B[p] = levNode(r, h-1, 3)
    
                    Q[p] = minQ
    
    
    
            # backtracking
                
            sentWerCount = 0.0
            sentSubCount = 0.0
            sentDelCount = 0.0
            sentInsCount = 0.0
    
            l = maxLength[nref]
            werRefWords = []
            werHypWords = []
            werRefErrors = []
            werHypErrors = []
            werRefAdd = []
            werHypAdd = []
    
            # 1) starting backtracking
            
            p = (len(refWords), len(hypWords))
    
            err = B[p].error
    
    
            if err != 0:
                if err == 1:
                    wer_errors(len(refWords), werRefWords, werRefAdd, werRefErrors, ref, addref, "sub")
                    wer_errors(len(hypWords), werHypWords, werHypAdd, werHypErrors, hyp, addhyp, "sub")
                    sentSubCount += 1
                elif err == 2:
                    wer_errors(len(refWords), werRefWords, werRefAdd, werRefErrors, ref, addref, "del")
                    sentDelCount += 1
                elif err == 3:
                    wer_errors(len(hypWords), werHypWords, werHypAdd, werHypErrors, hyp, addhyp, "ins")
                    sentInsCount += 1
                    
            else:
                wer_errors(len(refWords), werRefWords, werRefAdd, werRefErrors, ref, addref, "x")
                wer_errors(len(hypWords), werHypWords, werHypAdd, werHypErrors, hyp, addhyp, "x")
    
    
            # 2) going down
    
    
            rp = B[p].rpos
            hp = B[p].hpos
    
    
            while hp >= 0 and rp >= 0:
                p1 = (rp, hp)
                err = B[p1].error
    
                
                if err != 0:
                    if err == 1:
                        wer_errors(rp, werRefWords, werRefAdd, werRefErrors, ref, addref, "sub")
                        wer_errors(hp, werHypWords, werHypAdd, werHypErrors, hyp, addhyp, "sub")
                        sentSubCount += 1
                    elif err == 2:
                        wer_errors(rp, werRefWords, werRefAdd, werRefErrors, ref, addref, "del")
                        sentDelCount += 1
                    elif err == 3:
                        wer_errors(hp, werHypWords, werHypAdd, werHypErrors, hyp, addhyp, "ins")
                        sentInsCount += 1
                else:
                    wer_errors(rp, werRefWords, werRefAdd, werRefErrors, ref, addref, "x")
                    wer_errors(hp, werHypWords, werHypAdd, werHypErrors, hyp, addhyp, "x")
                    
                l -= 1
    
                hp = B[p1].hpos
                rp = B[p1].rpos
                
    
            
            # best (minimum) sentence WER => best reference => best WER errors
    
            sentWerCount = sentSubCount + sentDelCount + sentInsCount
            try:
                sentWer = sentWerCount/len(refWords)
            except ZeroDivisionError:
                logging.warn("Division by zero when calculating sentence WER")
                sentWer = float("Inf")
            if sentWer < minSentWer:
                minSentWer = sentWer
                bestWerRefIndex = ir
                bestWerRefLength = len(refWords)
                bestWerRefErrors = werRefErrors
                bestWerHypErrors = werHypErrors
                bestWerRefWords = werRefWords
                bestWerBaseRefWords = baseRefWords
                bestWerHypWords = werHypWords
                bestWerRefAdd = werRefAdd
                bestWerHypAdd = werHypAdd
                bestSentWer = sentWerCount
                
            nref += 1
    
            Q.clear()
            B.clear()
    
    
        self.totalWerRefLength += bestWerRefLength
        self.totalWerCount += bestSentWer
    
        bestWerRefErrors.reverse()
        bestWerHypErrors.reverse()
        bestWerRefWords.reverse()
        bestWerHypWords.reverse()
        bestWerRefAdd.reverse()
        bestWerHypAdd.reverse()
    
    
        # preparations for HPER and RPER
    
        refWords = refs[bestWerRefIndex].split()    
#        read_addfiles(addrtext, addrefs[bestWerRefIndex], refWords)
        baseRefWords = baserefs[bestWerRefIndex].split()
    
        if len(hypWords) == 0:
            hLen = 0.00000001
        else:
            hLen = len(hypWords)
    
    
        # HPER (hypothesis/precision) errors
        
        hperErrors = []
        sentHperCount = 0.0
        sentInflHperCount = 0.0
    
        hperErrors, sentHperCount, sentInflHperCount = hyp_ref_errors(refs[bestWerRefIndex], baserefs[bestWerRefIndex], hypWords, baseHypWords, "herr")
    
    
        sentHper = sentHperCount/hLen
        sentInflHper = sentInflHperCount/hLen
        
        
    
        # RPER (reference/recall) errors
            
        rperErrors = []
        sentRperCount = 0.0
        sentInflRperCount = 0.0
                
        rperErrors, sentRperCount, sentInflRperCount = hyp_ref_errors(hline, basehline, refWords, baseRefWords, "rerr")
        
        try:
            sentRper = sentRperCount/len(refWords)
            sentInflRper = sentInflRperCount/len(refWords)
        except ZeroDivisionError:
            logging.warn("Division by zero when calculating sentence Rper and sentInflRper")
            sentRper = float("Inf")          
            sentInflRper = float("Inf")    
    
        self.totalHperCount += sentHperCount
        self.totalRperCount += sentRperCount
        self.totalInflRperCount += sentInflRperCount
        self.totalInflHperCount += sentInflHperCount
     
        # preparations for error categorisation
        refErrorCats = []
        hypErrorCats = []
        
        sentMissCount = 0.0
        sentExtCount = 0.0
        sentRefLexCount = 0.0
        sentHypLexCount = 0.0
        sentRefReordCount = 0.0
        sentHypReordCount = 0.0
    
        sentBlockInflRperCount = 0.0
        sentBlockInflHperCount = 0.0
        sentBlockMissCount = 0.0
        sentBlockExtCount = 0.0
        sentRefBlockLexCount = 0.0
        sentHypBlockLexCount = 0.0
        sentRefBlockReordCount = 0.0
        sentHypBlockReordCount = 0.0
    
        
        # missing words, reference lexical errors, reference inflectional errors
        
    
        refErrorCats, sentMissCount, sentRefLexCount = miss_ext_lex(bestWerRefErrors, bestWerRefWords, rperErrors, refErrorCats, sentMissCount, sentRefLexCount, "miss")
    
    
        # extra words, hypothesis lexical errors, hypothesis inflectional errors
      
        hypErrorCats, sentExtCount, sentHypLexCount = miss_ext_lex(bestWerHypErrors, bestWerHypWords, hperErrors, hypErrorCats, sentExtCount, sentHypLexCount, "ext")
    
    
        # reordering errors
    
        hypErrorCats, sentHypReordCount = reord(bestWerRefErrors, bestWerRefWords, bestWerHypErrors, bestWerHypWords, hypErrorCats, sentHypReordCount)
    
        refErrorCats, sentRefReordCount = reord(bestWerHypErrors, bestWerHypWords, bestWerRefErrors, bestWerRefWords, refErrorCats, sentRefReordCount)
    
    
        # block error counts and error rates
    
        sentBlockInflRperCount = block_count(refErrorCats, "infl", sentBlockInflRperCount)
        sentBlockInflHperCount = block_count(hypErrorCats, "infl", sentBlockInflHperCount)
        sentBlockMissCount = block_count(refErrorCats, "miss", sentBlockMissCount)
        sentBlockExtCount = block_count(hypErrorCats, "ext", sentBlockExtCount)
        sentRefBlockReordCount = block_count(refErrorCats, "reord", sentRefBlockReordCount)
        sentHypBlockReordCount = block_count(hypErrorCats, "reord", sentHypBlockReordCount)
        sentRefBlockLexCount = block_count(refErrorCats, "lex", sentRefBlockLexCount)
        sentHypBlockLexCount = block_count(hypErrorCats, "lex", sentHypBlockLexCount)
    
        self.totalMissCount += sentMissCount
        self.totalExtCount += sentExtCount
        self.totalRefLexCount += sentRefLexCount
        self.totalHypLexCount += sentHypLexCount
        self.totalRefReordCount += sentRefReordCount
        self.totalHypReordCount += sentHypReordCount
    
        self.totalBlockInflRperCount += sentBlockInflRperCount
        self.totalBlockInflHperCount += sentBlockInflHperCount
        self.totalBlockMissCount += sentBlockMissCount
        self.totalBlockExtCount += sentBlockExtCount
        self.totalRefBlockReordCount += sentRefBlockReordCount
        self.totalHypBlockReordCount += sentHypBlockReordCount
        self.totalRefBlockLexCount += sentRefBlockLexCount
        self.totalHypBlockLexCount += sentHypBlockLexCount
    
    
        # write sentence error rates
        res = {}
        
        res['wer'] = 100*minSentWer        
        res['hper'] = 100*sentHper
        res['rper'] = 100*sentRper
 
        res['iHper'] = 100*sentInflHper
        res['iRper'] = 100*sentInflRper
        
        try:
            res['missErr'] = 100*sentMissCount/bestWerRefLength
            res['rLexErr'] = 100*sentRefLexCount/bestWerRefLength
            res['rRer'] = 100*sentRefReordCount/bestWerRefLength
            res['biRper'] = 100*sentBlockInflRperCount/bestWerRefLength
            res['rbRer'] =  100*sentRefBlockReordCount/bestWerRefLength
            res['bmissErr'] = 100*sentBlockMissCount/bestWerRefLength
            res['rbLexErr'] = 100*sentRefBlockLexCount/bestWerRefLength
        except ZeroDivisionError:
            logging.warn("Divison by zero when calculating missErr, rLexErr, rRer, biRper, rbRer, bmissErr, rbLexErr")
            for metricname in ['missErr', 'rLexErr', 'rRer', 'biRper', 'rbRer', 'bmissErr', 'rbLexErr']:
                res[metricname] = float("Inf")

        try:
            res['extErr'] = 100*sentExtCount/hLen
            res['hLexErr'] = 100*sentHypLexCount/hLen
            res['hRer'] = 100*sentHypReordCount/hLen
            res['biHper'] = 100*sentBlockInflHperCount/hLen
            res['hbRer'] = 100*sentHypBlockReordCount/hLen
            res['bextErr'] = 100*sentBlockExtCount/hLen
            res['hbLexErr'] = 100*sentHypBlockLexCount/hLen
        except ZeroDivisionError:
            logging.warn("Divison by zero when calculating 'extErr', 'hLexErr', 'hRer', 'biHper', 'hbRer', 'bextErr', 'hbLexErr'")

            for metricname in ['extErr', 'hLexErr', 'hRer', 'biHper', 'hbRer', 'bextErr', 'hbLexErr']:
                res[metricname] = float("Inf")


        res['aMissErr'] = sentMissCount
        res['aExtErr'] = sentExtCount
        res['arLexErr'] = sentRefLexCount
        res['arRer'] = sentRefReordCount
        
        res["refLength"] = bestWerRefLength
        res['TER'] = (sentMissCount + sentExtCount + sentRefLexCount + sentRefReordCount)*1.00/bestWerRefLength
        return res
    
    def calculate_total_scores(self):
        self.totalWer = 100*self.totalWerCount/self.totalWerRefLength
        self.totalHper = 100*self.totalHperCount/self.totalHypLength
        self.totalRper = 100*self.totalRperCount/self.totalWerRefLength
        
        self.totalInflHper = 100*self.totalInflHperCount/self.totalHypLength
        self.totalInflRper = 100*self.totalInflRperCount/self.totalWerRefLength
        self.totalMissErr = 100*self.totalMissCount/self.totalWerRefLength
        self.totalExtErr = 100*self.totalExtCount/self.totalHypLength
        self.totalrLexErr = 100*self.totalRefLexCount/self.totalWerRefLength
        self.totalhLexErr = 100*self.totalHypLexCount/self.totalHypLength
        self.totalrRer = 100*self.totalRefReordCount/self.totalWerRefLength
        self.totalhRer = 100*self.totalHypReordCount/self.totalHypLength
        
        self.totalbiHper = 100*self.totalBlockInflHperCount/self.totalHypLength
        self.totalbiRper = 100*self.totalBlockInflRperCount/self.totalWerRefLength
        self.totalrbRer = 100*self.totalRefBlockReordCount/self.totalWerRefLength
        self.totalhbRer = 100*self.totalHypBlockReordCount/self.totalHypLength
        self.totalbmissErr = 100*self.totalBlockMissCount/self.totalWerRefLength
        self.totalbextErr = 100*self.totalBlockExtCount/self.totalHypLength
        self.totalrbLexErr = 100*self.totalRefBlockLexCount/self.totalWerRefLength
        self.totalhbLexErr = 100*self.totalHypBlockLexCount/self.totalHypLength
    
    
        # write wer, rper and hper words (and additional information, such as POS, etc.)
    
#        if errfile:
#            write_error_words(errftxt, addrtext, bestWerRefErrors, bestWerRefWords, bestWerRefAdd, str(nSent)+"::wer-ref-errors: ")
#            write_error_words(errftxt, addhtext, bestWerHypErrors, bestWerHypWords, bestWerHypAdd, str(nSent)+"::wer-hyp-errors: ")
#    
#            errftxt.write("\n")
#    
#            write_error_words(errftxt, addrtext, rperErrors, refWords, addrefWords, str(nSent)+"::ref-errors: ")
#            write_error_words(errftxt, addhtext, hperErrors, hypWords, addhypWords, str(nSent)+"::hyp-errors: ")
#    
#            errftxt.write("\n\n")
#    
#    
#        # write error categories (and additional information, such as POS, etc.)
#    
#        if errcatfile:
#            write_error_cats(errcatfile, errcftxt, addrtext, refWords, bestWerRefAdd, refErrorCats, "ref")
#            write_error_cats(errcatfile, errcftxt, addhtext, hypWords, bestWerHypAdd, hypErrorCats, "hyp")
#    
#        if htmlfile:
#            write_html(htmlfile, htmltxt, addrtext, refWords, bestWerRefAdd, refErrorCats, "ref")
#            write_html(htmlfile, htmltxt, addhtext, hypWords, bestWerHypAdd, hypErrorCats, "hyp")
#    
class BinaryHjerson(Hjerson):
    def analyze(self, hline, basehline, addhline, refs, baserefs, addrefs):
        features = super(BinaryHjerson, self).analyze(hline, basehline, addhline, refs, baserefs, addrefs)
        newfeatures = {}
        for name, value in features.iteritems():
            if value > 0:
                newfeatures[name] = 1
            else:
                newfeatures[name] = 0
        return newfeatures
            


class levNode:
    def __init__(self, rpos=0, hpos=0, error=0):
        self.rpos = rpos
        self.hpos = hpos
        self.error = error


def read_addfiles(addtext, addline, words):
    if addtext:
        addwords = addline.split()
    else:
        addwords = ["" for x in range(len(words))]
    return addwords

def adjust_indices(words, adjwords, addwords, adjaddwords):
    i = 1
    while i <= len(words):
        adjwords[i] = words[i-1]
        adjaddwords[i] = addwords[i-1]
        i += 1


def wer_errors(index, werwords, weradd, wererr, words, add, error):
    werwords.append(words[index])
    weradd.append(add[index])
    wererr.append(error)

def hyp_ref_errors(rline, rbaseline, hwords, hbases, error):
    
    rwords = rline.split()
    logging.debug("{}\t{}".format(len(hwords), hwords))
    logging.debug("{}\t{}".format(len(hbases), hbases))
    rbases = rbaseline.split()
    errors = []
    errorcount = 0.0
    inflerrorcount = 0.0

    for ihw, hw in enumerate(hwords):
        if hw in rwords:
            errors.append("x")
            n = rwords.index(hw)
            del rwords[n]
            del rbases[n]
        else:
            errors.append(error)
            errorcount += 1

    for ihb, hb in enumerate(hbases):
        if hb in rbases:
            if errors[ihb] == error:
                errors[ihb] = "i"+error
                n = rbases.index(hb)
                del rbases[n]
                inflerrorcount += 1
     
    return errors, errorcount, inflerrorcount
   

def miss_ext_lex(wererrors, werwords, pererrors, errcats, misextcount, lexcount, misext):
    i = 0
    while i < len(wererrors):
        refWerWord = werwords[i]
        refWerError = wererrors[i]
        rperError  = pererrors[i]
        if rperError == "irerr" or rperError == "iherr":
            errcats.append("infl")
        elif rperError == "rerr" or rperError == "herr":
            if refWerError == "del" or refWerError == "ins":
                errcats.append(misext)
                misextcount += 1
            elif refWerError == "sub":
                errcats.append("lex")
                lexcount += 1
            else:
                errcats.append("x")
        else:
            errcats.append("x")
        i += 1

    return errcats, misextcount, lexcount

def reord(werreferrors, werrefwords, werhyperrors, werhypwords, hyperrcats, hypcount):
    referr = []
    i = 0
    while i < len(werreferrors):
        if werreferrors[i] != "x":
            referr.append(werrefwords[i])
        i += 1

    i = 0
    while i < len(werhyperrors):
        hypWerWord = werhypwords[i]
        hypWerError = werhyperrors[i]
        if hypWerError == "ins" or hypWerError == "del" or hypWerError == "sub":
            if hypWerWord in referr:
                hyperrcats[i] = "reord"
                hypcount += 1
                n = referr.index(hypWerWord)
                del referr[n]
        i += 1

    return hyperrcats, hypcount

def block_count(errcats, errcat, blockcount):
    i = 0
    newblock = True
    while i < len(errcats):
        cat = errcats[i]
        if cat == errcat:
            if newblock == True:
                blockcount += 1
                newblock = False
        else:
            newblock = True
            
        i += 1

    return blockcount


def write_error_rates(text, errorname, errorcount, errorrate):
    text.write(errorname+"\t"+str("%.0f" % errorcount)+"\t"+str("%.2f" % errorrate)+"\n")

def write_error_words(text, addtext, errors, words, add, title):
    text.write(title)
    for nr, r in enumerate(errors):
        if addtext:
            text.write(words[nr]+"#"+add[nr]+"~~"+r+" ")
        else:
            text.write(words[nr]+"~~"+r+" ")

    text.write("\n")


if __name__ == '__main__':
    h = Hjerson(lang="en")
    hyp = 'En lugar de ello , es algo tan terrible como " un condenado estrangulado en secreto " .'
    ref = 'En lugar de ello , es terriblemente como " un condenado estrangulados en secreto . "'
    print h.get_features_strings(hyp, [ref])
