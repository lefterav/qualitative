"""

@author: Eleftherios Avramidis
"""

from multirankeddataset import MultiRankedDataset
import logging
import sys
from collections import OrderedDict
import numpy
from ranking import Ranking
from evaluation.ranking.segment import kendall_tau, kendall_tau_prob
from evaluation.ranking.set import *
from evaluation.ranking.tau import SegmentLevelData
from operator import methodcaller, xor

SET_METRIC_FUNCTIONS = [kendall_tau_set,
                        kendall_tau_set_no_ties,
                        mrr,
                        avg_ndgc_err, 
                        best_predicted_vs_human,
                        avg_predicted_ranked 
                        ]

REFERENCE_METRIC_ATTRIBUTES  = {
                                "ref-bleu" : True,
#                                "ref-meteor_fragPenalty" : True,
#                                "ref-meteor_precision" : True,
#                                "ref-meteor_recall" : True,
                                "ref-meteor_score" : True,
                                "ref-rgbF" : True,
#                                "ref-rgbPrec" : True,
#                                "ref-rgbRec" : True,
                                "ref-wer" : False,
#                                "ref-hj_aExtErr" : False,
#                                "ref-hj_aMissErr" : False,
#                                "ref-hj_arLexErr" : False,
#                                "ref-hj_arRer" : False,
#                                "ref-hj_bextErr" : False,
#                                "ref-hj_biHper" : False,
#                                "ref-hj_biRper" : False,
#                                "ref-hj_bmissErr" : False,
#                                "ref-hj_extErr" : False,
#                                "ref-hj_hbLexErr" : False,
#                                "ref-hj_hbRer" : False,
#                                "ref-hj_hLexErr" : False,
#                                "ref-hj_hper" : False,
#                                "ref-hj_iHper" : False,
#                                "ref-hj_iRper" : False,
#                                "ref-hj_missErr" : False,
#                                "ref-hj_rbLexErr" : False,
#                                "ref-hj_rbRer": False,
#                                "ref-hj_rLexErr" : False,
#                                "ref-hj_rper" : False,
#                                "ref-hj_rRer" : False,
                                "ref-hj_TER" : False,
#                                "ref-hj_wer" : False,
#                                "ref-hj_hRer" : False
}

FULL_BOOTSTRAP_SAMPLES = 10
                                

def get_metrics_scores(data, predicted_rank_name, original_rank_name,
                       invert_ranks = False,
                       filter_ref = True,
                       suffix = "",
                       prefix = "", 
                       **kwargs):
    """
    Calculates all metrics 
    @param predicted_rank_name: the name of the attribute containing the predicted rank
    @type predicted_rank_name: str 
    @param original_rank_name: the name of the attribute containing the human rank
    @type original_rank_name: str
    @param filter_ref: don't include reference sentences when existing in the pairs
    @type filter_ref: boolean
    @param exclude_ties: don't include human ties in the calculation, even if correctly predicted
    @type exclude_ties: boolean
    @return: the Kendall tau score and the probability for the null hypothesis of X and Y being independent
    @rtype: tuple(float, float)
    """
    stats = OrderedDict()
    stats.update(get_ranking_scores(data, predicted_rank_name, original_rank_name, invert_ranks, filter_ref, suffix, prefix))
    stats.update(get_wmt_scores(data, predicted_rank_name, original_rank_name, invert_ranks, filter_ref, suffix, prefix))
    return stats


def get_baseline_scores(data, original_rank_name,
                           filter_ref = True,
                           suffix = "",
                           prefix = "", 
                           invert_ranks = False,
                           **kwargs):

    stats = OrderedDict()
    for baseline_name in ["fixed", "random", "random_noties", "alphabetical", "alphabetical_inv"]:
        invert_ranks = invert_ranks
        baseline_prefix = "_".join([prefix, baseline_name])
        stats.update(get_baseline_ranking_scores(data, baseline_name, original_rank_name, invert_ranks, filter_ref, suffix, prefix=baseline_prefix))
    logging.info("Calculating wmt baseline scores")
    stats.update(get_baseline_wmt_scores(data, original_rank_name, invert_ranks, filter_ref, suffix, prefix=prefix))

    for metric_name, metric_inverted in REFERENCE_METRIC_ATTRIBUTES.iteritems():
        metric_prefix = "_".join([prefix, metric_name])
        invert_these_ranks = (bool(invert_ranks)!=bool(metric_inverted)) 
        #TODO: clarify what happens when class is an error metric; maybe reverse either predicted or original rank, depending on which one is an error metric

        logging.info("Calculating scores for ref-based {}".format(metric_name))
        stats.update(get_ranking_scores(data, metric_name, original_rank_name, invert_these_ranks, filter_ref, suffix, prefix=metric_prefix))
        logging.info("Calculating WMT scores ref-based {}".format(metric_name))
        stats.update(get_wmt_scores(data, metric_name, original_rank_name, invert_these_ranks, filter_ref, suffix, prefix=metric_prefix))
    return stats


def get_baseline_ranking_scores(data, baseline_name, original_rank_name,
                       invert_ranks = False,
                       filter_ref = True,
                       suffix = "",
                       prefix = "",
                       **kwargs):
    
    predicted_rank_vectors = []
    original_rank_vectors = []
    
    for parallelsentence in data.get_parallelsentences():

        if filter_ref:
            #get a vector with all the rank labels from all systems apart from the references
            original_rank_vector = parallelsentence.get_filtered_target_attribute_values(original_rank_name, 
                                                                                        filter_attribute_name="system", 
                                                                                        filter_attribute_value="_ref")
        else:
            original_rank_vector = parallelsentence.get_target_attribute_values(original_rank_name)
            
        ranking_length = len(original_rank_vector)
        if baseline_name == "fixed":
            predicted_rank_vector = [1] * ranking_length
        elif baseline_name == "random":
            random.seed()
            predicted_rank_vector = [random.randint(1, ranking_length) for i in range(ranking_length)]
        elif baseline_name == "random_noties": 
            random.seed()
            predicted_rank_vector = range(1, ranking_length+1)
            random.shuffle(predicted_rank_vector)
        elif baseline_name == "alphabetical":
            system_names = parallelsentence.get_filtered_target_attribute_values("system", filter_attribute_name="system", filter_attribute_value="_ref")
            sorted_system_names = sorted(system_names)
            predicted_rank_vector = [sorted_system_names.index(name)+1 for name in system_names]
        elif baseline_name == "alphabetical_inv":
            system_names = parallelsentence.get_filtered_target_attribute_values("system", filter_attribute_name="system", filter_attribute_value="_ref")
            sorted_system_names = sorted(system_names, reverse=True)
            predicted_rank_vector = [sorted_system_names.index(name)+1 for name in system_names]   
        else:
            raise Exception("You provided a baseline name that is not supported {}".format(baseline_name))
        try:
            predicted_ranking = Ranking(predicted_rank_vector)
            original_ranking = Ranking(original_rank_vector)
            #invert rankings if requested
            if invert_ranks:
                predicted_ranking = predicted_ranking.reverse()
                #original_ranking = original_ranking.reverse()
        except Exception as e:
            logging.error("Error while processing Parallelsentence with attributes {}".format(parallelsentence.get_attributes()))
            logging.error("ranking that caused the error: predicted: {}, original: {}".format(predicted_ranking, original_ranking))
            raise Exception(e)

        #add the ranking in the big vector with all previous parallel sentences
        predicted_rank_vectors.append(predicted_ranking)
        original_rank_vectors.append(original_ranking)

    stats = OrderedDict()
    
    #process the list of rankings with all metric functions and collect the
    #results in an ordered dict
    for callback in SET_METRIC_FUNCTIONS:
        current_stats = callback(predicted_rank_vectors, original_rank_vectors)
        stats.update(current_stats)
        
    #add the requested preffix and suffix to every value    
    stats = OrderedDict([("{}-{}{}".format(prefix, key, suffix),value) for key,value in stats.iteritems()])
    return stats
        

def get_ranking_scores(data, predicted_rank_name, original_rank_name,
                       invert_ranks = False,
                       filter_ref = True,
                       suffix = "",
<<<<<<< HEAD
                       prefix = "", 
=======
                       prefix = "",
<<<<<<< ssst14
<<<<<<< ssst14
<<<<<<< HEAD
=======
=======
>>>>>>> refs/remotes/origin/ssst14
>>>>>>> e35537c Separate a function to make it more functional
                       replace_predicted = None,
>>>>>>> e35537ccbe283736307842b113e075ba6fa22d29
=======
>>>>>>> refs/remotes/origin/ssst14
                       replace_predicted = None,
>>>>>>> 2257519 local modifications
                       **kwargs):
    predicted_rank_vectors = []
    original_rank_vectors = []
    missing_predicted_values = 0

    for parallelsentence in data.get_parallelsentences():

        if filter_ref:
            #get a vector with all the rank labels from all systems apart from the references
            try:
                predicted_rank_vector = parallelsentence.get_filtered_target_attribute_values(predicted_rank_name, 
                                                                                         filter_attribute_name="system", 
                                                                                         filter_attribute_value="_ref")
            except Exception as e:
                logging.error("Could not get desired rank_name '{}' from parallelsentence with attributes: \n{}".format(predicted_rank_name, parallelsentence.get_attributes()))
                missing_predicted_values += 1
                raise Exception(e)

            original_rank_vector = parallelsentence.get_filtered_target_attribute_values(original_rank_name, 
                                                                                        filter_attribute_name="system", 
                                                                                        filter_attribute_value="_ref")
        else:
            #get a vector with all the rank labels
<<<<<<< HEAD
            predicted_rank_vector = parallesentence.get_target_attribute_values(predicted_rank_name)
            original_rank_vector = parallesentence.get_target_attribute_values(original_rank_name)            
            
=======
            predicted_rank_vector = parallelsentence.get_target_attribute_values(predicted_rank_name)
            original_rank_vector = parallelsentence.get_target_attribute_values(original_rank_name)
>>>>>>> refs/remotes/origin/ssst14
        #construct ranking objects

        
        try:
            predicted_ranking = Ranking(predicted_rank_vector)
            original_ranking = Ranking(original_rank_vector)
            #invert rankings if requested
            if invert_ranks:
                predicted_ranking = predicted_ranking.reverse()
                #original_ranking = original_ranking.reverse()
        except Exception as e:
            logging.error("Error while processing Parallelsentence with attributes {}".format(parallelsentence.get_attributes()))
            logging.error("ranking that caused the error: predicted: {}, original: {}".format(predicted_ranking, original_ranking))
            raise Exception(e)

        #add the ranking in the big vector with all previous parallel sentences
        predicted_rank_vectors.append(predicted_ranking)
        original_rank_vectors.append(original_ranking)

    if missing_predicted_values:
        logging.warning("{} sentences where missing the {}".format(missing_predicted_values, predicted_rank_name))
    stats = OrderedDict()
    
    #process the list of rankings with all metric functions and collect the
    #results in an ordered dict
    for callback in SET_METRIC_FUNCTIONS:
        current_stats = callback(predicted_rank_vectors, original_rank_vectors)
        stats.update(current_stats)
        
    #add the requested preffix and suffix to every value    
    stats = OrderedDict([("{}-{}{}".format(prefix, key, suffix),value) for key,value in stats.iteritems()])
    return stats
    
import random
import time

def get_wmt_scores(data, predicted_rank_name, original_rank_name,
                       invert_ranks = False,
                       filter_ref = True,
                       suffix = "",
                       prefix = "",
                       variants_with_confidence = ["wmt12", "wmt14"],
                       variants_no_confidence = ["wmt13"],
                       direction = "dummy",
                       **kwargs):
    
    wmtdata = SegmentLevelData()
    metric = "autoranking"
    direction = "dummy"
    
    count_length = defaultdict(int)
        
    for parallelsentence in data.get_parallelsentences():
        #lang_pair = parallelsentence.get_langpair()
        lang_pair = "dummy"
        segment = int(parallelsentence.get_id())

        pairwise_parallelsentences = parallelsentence.get_pairwise_parallelsentences(class_name=original_rank_name)
        
        translations = parallelsentence.get_translations()
        ranking_length = len(translations)
        count_length[ranking_length] += 1
        
        # First populate the structure for the human ratings  
        for pairwise_parallelsentence in pairwise_parallelsentences:
            translation1 = pairwise_parallelsentence.get_translations()[0]
            system_id1 = translation1.get_system_name()
            human_rank1 = float(translation1.get_attribute(original_rank_name))            
            
            translation2 = pairwise_parallelsentence.get_translations()[1]
            system_id2 = translation2.get_system_name()
            human_rank2 = float(translation2.get_attribute(original_rank_name))
            
            compare = lambda x, y: '<' if x < y else '>' if x >  y else '='
            extracted_comparisons = [
                (segment, system_id1, system_id2, compare(human_rank1, human_rank2), ranking_length)
            ]
            wmtdata.human_comparisons[lang_pair] += extracted_comparisons
        
        for translation in translations:
            system_id = translation.get_system_name()
            predicted_rank_value = translation.get_attribute(predicted_rank_name)
            if invert_ranks:
                predicted_rank = float(predicted_rank_value)
            else:
                predicted_rank = -1.00 * float(predicted_rank_value)
            wmtdata.metrics_data[metric,lang_pair][system_id][segment] = predicted_rank
            #wmtdata.metrics_data[metric,lang_pair][system_id][segment] = predicted_rank
    
    scores = OrderedDict()
    for variant in variants_with_confidence:
        tau, confidence, weighed_tau, pvalue = wmtdata.compute_tau_confidence(metric, direction, variant, count_length, samples=FULL_BOOTSTRAP_SAMPLES)
        scores["tau_{}".format(variant)] = tau
        scores["tau_{}_conf".format(variant)] = confidence
        scores["tau_{}_weighed".format(variant)] = weighed_tau
        scores["tau_{}_p-value".format(variant)] = pvalue
        
    for variant in variants_no_confidence:
        tau, confidence, weighed_tau, pvalue = wmtdata.compute_tau_confidence(metric, direction, variant, count_length, samples=0)
        scores["tau_{}".format(variant)] = tau
        scores["tau_{}_weighed".format(variant)] = weighed_tau
        scores["tau_{}_p-value".format(variant)] = pvalue

    scores = OrderedDict([("{}-{}{}".format(prefix, key, suffix),value) for key,value in scores.iteritems()])        
    return scores



            

def get_baseline_wmt_scores(data, original_rank_name,
                       invert_ranks = False,
                       filter_ref = True,
                       suffix = "",
                       prefix = "",
                       variants = ["wmt12", "wmt13", "wmt14"],
                       direction = "dummy",
                       **kwargs):
    
    wmtdata = SegmentLevelData()
    random.seed(int(time.time()))
    direction = "dummy"
    
    count_length = defaultdict(int)        
    for parallelsentence in data.get_parallelsentences():
        #lang_pair = parallelsentence.get_langpair()
        lang_pair = "dummy"
        segment = int(parallelsentence.get_id())
    
        translations = parallelsentence.get_translations()
        ranking_length = len(translations)
        count_length[ranking_length] += 1

        pairwise_parallelsentences = parallelsentence.get_pairwise_parallelsentences(class_name=original_rank_name)
        
        for pairwise_parallelsentence in pairwise_parallelsentences:
            translation1 = pairwise_parallelsentence.get_translations()[0]
            system_id1 = translation1.get_system_name()
            human_rank1 = int(translation1.get_attribute(original_rank_name))            
            
            translation2 = pairwise_parallelsentence.get_translations()[1]
            system_id2 = translation2.get_system_name()
            human_rank2 = int(translation2.get_attribute(original_rank_name))
            
            compare = lambda x, y: '<' if x < y else '>' if x > y else '='
            extracted_comparisons = [
                (segment, system_id1, system_id2, compare(human_rank1, human_rank2))
            ]
            wmtdata.human_comparisons[lang_pair] += extracted_comparisons
        
        i = 0
        
        for translation in sorted(translations, key=methodcaller("get_system_name")):
            system_id = translation.get_system_name()
            
            random_rank = random.randint(1, ranking_length)
            wmtdata.metrics_data["random", lang_pair][system_id][segment] = random_rank
            
            wmtdata.metrics_data["fixed", lang_pair][system_id][segment] = 1
            0
            i += 1
            wmtdata.metrics_data["alphabetical", lang_pair][system_id][segment] = i
            wmtdata.metrics_data["alphabetical_inv", lang_pair][system_id][segment] = -1.0 * i
 
    scores = OrderedDict()
    for metric in ["fixed", "random", "alphabetical", "alphabetical_inv"]:
        for variant in variants:
            tau, confidence, weighed_tau, pvalue = wmtdata.compute_tau_confidence(metric, direction, variant, count_length, samples=FULL_BOOTSTRAP_SAMPLES)
            if tau is None:
                raise Exception("tau is None")
            this_prefix = "_".join([prefix, metric])
            scores["base_{}_tau_{}".format(this_prefix, variant)] = tau
            scores["base_{}_tau_{}_conf".format(this_prefix, variant)] = confidence
            scores["base_{}_tau_{}_weighed".format(this_prefix, variant)] = weighed_tau
            scores["base_{}_tau_{}_p-value".format(this_prefix, variant)] = pvalue
    return scores

class Scoring(MultiRankedDataset):
    """
    classdocs
    """
    def __init__(self, *params, **kwargs):
        #get global setting for reversing ranks
        self.invert_ranks = kwargs.setdefault("invert_ranks", False)
        #fire parent constructor
        super(Scoring, self).__init__(*params)
        
    
    def get_systems_scoring_from_segment_ranks(self, rank_attribute_name):
        
        """
        Provides a performance score for every system. The score is the percentage of times the system
        performed better than all other systems or equally to the systems that performed better than all other systems
        @param rank_attribute_name: the name of the target sentence attribute which contains the rank value, that we compare upon 
        Smaller rank means better system.  
        @type rank_attribute_name: string
        @return A map of the system names and their performance percentage
        """
        systems_performance = {}
        for parallelsentence in self.parallelsentences:
            rank_per_system = {}
            #first sort the ranks by system
            for target in parallelsentence.get_translations():
                system = target.get_attribute("system")
                rank = int(float(target.get_attribute(rank_attribute_name)))
                rank_per_system[system] = rank
            #then count the times a system performs as best
            for system in rank_per_system:
                if rank_per_system[system] == min(rank_per_system.values()):
                    try:
                        systems_performance[system] += 1
                    except KeyError:
                        systems_performance[system] = 1
        #finally calculate the percentage that each system, scored as best
        for system in systems_performance:
            systems_performance[system] = 1.00 * systems_performance[system] / len(self.parallelsentences)
        return systems_performance
    
    def get_spearman_correlation(self, rank_name_1, rank_name_2):
        from scipy.stats import spearmanr
        """
        Calculates the system-level Spearman rank correlation given two sentence-level features, i.e. 
        the human and the estimated rank of each parallelsentence 
        @param rank_name_1: the name of the target sentence attribute containing the first rank value
        @type rank_name_1: string
        @param rank_name_2: the name of the target sentence attribute containing the second rank value
        @type rank_name_2: string
        @return the Spearman correlation rho and p value
        """
        systems_evaluation_1 = self.get_systems_scoring_from_segment_ranks(rank_name_1)
        systems_evaluation_2 = self.get_systems_scoring_from_segment_ranks(rank_name_2)
        #print systems_evaluation_1
        #print systems_evaluation_2
        rank_evaluation_1 = []
        rank_evaluation_2 = []
        for (system, rank_1) in systems_evaluation_1.items():
            rank_evaluation_1.append(rank_1)
            rank_2 = systems_evaluation_2[system]
            rank_evaluation_2.append(rank_2)
        #print "rank------" 
        #print rank_evaluation_1
        #print rank_evaluation_2
        return spearmanr(rank_evaluation_1, rank_evaluation_2)
    
    def get_metrics_scores(self, predicted_rank_name, original_rank_name, **kwargs):
        return get_metrics_scores(self, predicted_rank_name, original_rank_name, invert_ranks = self.invert_ranks, **kwargs)

    
    
    

    
    
    def get_kendall_tau_vector(self, rank_name_1, rank_name_2):
        from scipy.stats import kendalltau

        taus = []
        pis = []
        for parallelsentence in self.parallelsentences:
            rank_vector_1 = parallelsentence.get_target_attribute_values(rank_name_1)
            rank_vector_2 = parallelsentence.get_target_attribute_values(rank_name_2)
            
            fullscore = kendalltau(rank_vector_1, rank_vector_2)
            tau = fullscore[0]
            pi = fullscore[1]
            taus.append(tau)
            pis.append(pi)
        return taus, pis
    
    def get_kendall_tau_avg(self, rank_name_1, rank_name_2):
        taus, pis = self.get_kendall_tau_vector(rank_name_1, rank_name_2)
        avg = sum(taus)/len(taus)
        pi = min(pis)
        return avg, pi
    
    def get_kendall_tau_freq(self, rank_name_1, rank_name_2):
        taus = self.get_kendall_tau_vector(rank_name_1, rank_name_2)[0]
        frequency = {}
        for tau in taus:
            try:
                frequency[tau] += 1
            except KeyError:
                frequency[tau] = 0
        return frequency 
            
    def selectbest_accuracy(self, estimated_rank_name, original_rank_name):
        truepositive_withfirsteffort = 0.00
        truepositive_withanyeffort = 0.00
        pairwise_comparisons = 0.00
        for parallelsentence in self.parallelsentences:
            estimated_rank_vector = parallelsentence.get_target_attribute_values(estimated_rank_name)
            original_rank_vector = parallelsentence.get_target_attribute_values(original_rank_name)
            
            true_positive = 0.00
            false_positive = 0.00
            alreadyfoundfirst = False
            
            for i in range(len(estimated_rank_vector)):
                if int(estimated_rank_vector[i]) == 1:
                    pairwise_comparisons += 1
                    if int(original_rank_vector[i]) == 1:
                        true_positive += 1
                        if not alreadyfoundfirst:
                            truepositive_withfirsteffort +=1
                    else:
                        false_positive += 1
                    alreadyfoundfirst = True
            if true_positive > 0 : 
                truepositive_withanyeffort +=1
            

                    
        accuracy_firsteffort = truepositive_withfirsteffort/len(self.parallelsentences)
        accuracy_anyeffort = truepositive_withanyeffort / len(self.parallelsentences)
        return (accuracy_firsteffort, accuracy_anyeffort)
    
    def normalize_rank_list(self, rank_list):
        """
        Normalizes a rank list so that it doesn't contain gaps. E.g [1,3,3,4] will be converted to [1,2,2,3]
        
        """
    
    
    def best_predicted_vs_human(self, predicted_rank_name, original_rank_name):
        from numpy import average
        actual_values_of_best_predicted = {}
        
        if self.invert_ranks:
            inv = -1.00
        else:
            inv = 1.00
        
        for parallelsentence in self.parallelsentences:
            predicted_rank_vector = parallelsentence.get_filtered_target_attribute_values(predicted_rank_name, "system", "_ref")
            original_rank_vector = parallelsentence.get_filtered_target_attribute_values(original_rank_name, "system", "_ref")
            
            #make sure we are dealing with numbers      
            predicted_rank_vector = [float(v) for v in predicted_rank_vector]
            original_rank_vector = [inv*float(v) for v in original_rank_vector]
            
            if not predicted_rank_vector:
                continue
            best_predicted_rank = min(predicted_rank_vector)
            original_rank_order = sorted(original_rank_vector)
            
            
                
            original_ranks = []
            for original_rank, predicted_rank in zip(original_rank_vector, predicted_rank_vector):
                if predicted_rank == best_predicted_rank:
                    corrected_original_rank = original_rank_order.index(original_rank) + 1
                    original_ranks.append(corrected_original_rank)
                    
                
            selected_original_rank = max(original_ranks)
            a = actual_values_of_best_predicted.setdefault(selected_original_rank, 0)
            actual_values_of_best_predicted[selected_original_rank] = a + 1
                    
        n = len(self.parallelsentences)
        percentages = {}
        total = 0
        for rank, counts in  actual_values_of_best_predicted.iteritems():
            percentages[rank] = round(100.00 * counts / n , 2 )
            total += counts
        return percentages
           
    def mrr(self, predicted_rank_name, original_rank_name):
        from numpy import average

        if self.invert_ranks:
            nv = -1.00
        else:
            inv = 1.00
        
        reciprocal_ranks = []
        
        for parallelsentence in self.parallelsentences:
            predicted_rank_vector = parallelsentence.get_filtered_target_attribute_values(predicted_rank_name, "system", "_ref")
            original_rank_vector = parallelsentence.get_filtered_target_attribute_values(original_rank_name, "system", "_ref")
            
            #make sure we are dealing with numbers      
            predicted_rank_vector = [float(v) for v in predicted_rank_vector]
            original_rank_vector = [inv*float(v) for v in original_rank_vector]
            
            if not predicted_rank_vector:
                continue
            best_original_rank = min(original_rank_vector)
            predicted_rank_order = sorted(predicted_rank_vector)
            
                
            predicted_ranks = []
            for original_rank, predicted_rank in zip(original_rank_vector, predicted_rank_vector):
                if predicted_rank == best_original_rank:
                    try: #todo: check why this fails and may be reason for wrong calcs
                        corrected_predicted_rank = predicted_rank_order.index(original_rank) + 1
                        predicted_ranks.append(corrected_predicted_rank)
                    except:
                        pass
                    
            #get the worse predicted (in case of ties)
            selected_original_rank = max(predicted_ranks)
            reciprocal_ranks.append(1.00/selected_original_rank)
                    
        n = len(self.parallelsentences)
        return average(reciprocal_ranks)
    
    
    def avg_predicted_ranked(self, predicted_rank_name, original_rank_name):
        return self.avg_first_ranked(original_rank_name, predicted_rank_name)
    
    def avg_first_ranked(self, predicted_rank_name, original_rank_name):
        """
        Provide an integer that shows the predicted rank of the best system
        It is averaged over all segments. Tied predictions are penalized
        """
        from numpy import average
        corresponding_ranks = []
        
        if self.invert_ranks:
            inv = -1.00
        else:
            inv = 1.00
        
        for parallelsentence in self.parallelsentences:
            predicted_rank_vector = parallelsentence.get_filtered_target_attribute_values(predicted_rank_name, "system", "_ref")
            original_rank_vector = parallelsentence.get_filtered_target_attribute_values(original_rank_name, "system", "_ref")
            
            #make sure we are dealing with numbers      
            predicted_rank_vector = [float(v) for v in predicted_rank_vector]
            original_rank_vector = [inv*float(v) for v in original_rank_vector]
            
            best_original_rank = min(original_rank_vector)
            predicted_rank_order = sorted(predicted_rank_vector)
                        
            
#            print original_rank_vector, predicted_rank_vector, 
            
            current_corresponding_ranks = []
            for original_rank, predicted_rank in zip(original_rank_vector, predicted_rank_vector):
                if original_rank == best_original_rank:
                    #if counting of ranks starts higher than 1, then this should fix it
                    predicted_rank_normalized =  predicted_rank_order.index(predicted_rank) 
                    #penalize ties
                    #if the best system was found first, but the same rank was predicted for another 4 system outputs, then rank = 5
                    penalized_rank = predicted_rank_normalized + predicted_rank_vector.count(predicted_rank) 
#                    penalized_rank = corresponding_rank
                    current_corresponding_ranks.append(penalized_rank)
#                    print predicted_rank, penalized_rank
                    #it is enough to calculate this once per sentence
#            if current_corresponding_ranks :
            corresponding_ranks.append(average(current_corresponding_ranks))
                        
        first_ranked = average(corresponding_ranks)
        return first_ranked
       

    
    def get_kendall_tau(self, predicted_rank_name, original_rank_name, **kwargs):
        """
        Calculates average Kendall tau of predicted vs human ranking according to WMT12 (Birch et. al 2012)
        @param predicted_rank_name: the name of the attribute containing the predicted rank
        @type predicted_rank_name: str 
        @param original_rank_name: the name of the attribute containing the human rank
        @type original_rank_name: str
        @param filter_ref: don't include reference sentences when existing in the pairs
        @type filter_ref: boolean
        @param exclude_ties: don't include human ties in the calculation, even if correctly predicted
        @type exclude_ties: boolean
        @return: the Kendall tau score and the probability for the null hypothesis of X and Y being independent
        @rtype: tuple(float, float)
        """
        import itertools
        import numpy as np
        
        #filter references by default unles otherwise specified
        filter_ref = kwargs.setdefault("filter_ref", True)
        suffix = kwargs.setdefault("suffix", "")
        prefix = kwargs.setdefault("prefix", "")
        kwargs["invert_ranks"] = self.invert_ranks
        
        segtaus = []
        segprobs = []
        
        concordant = 0
        discordant = 0
        valid_pairs = 0
        original_ties_overall = 0
        predicted_ties_overall = 0
        pairs_overall = 0
        sentences_with_ties = 0
        
        for parallelsentence in self.parallelsentences:
            if filter_ref:
                predicted_rank_vector = parallelsentence.get_filtered_target_attribute_values(predicted_rank_name, "system", "_ref")
                original_rank_vector = parallelsentence.get_filtered_target_attribute_values(original_rank_name, "system", "_ref")
            else:
                predicted_rank_vector = parallelsentence.get_target_attribute_values(predicted_rank_name)
                original_rank_vector = parallelsentence.get_target_attribute_values(original_rank_name)
            segtau, segprob, concordant_count, discordant_count, all_pairs_count, original_ties, predicted_ties, pairs = kendall_tau(predicted_rank_vector, original_rank_vector, **kwargs)
            if segtau and segprob:
                segtaus.append(segtau)
                segprobs.append(segprob)
                
            concordant += concordant_count
            discordant += discordant_count
            valid_pairs += all_pairs_count
            
            original_ties_overall += original_ties
            predicted_ties_overall += predicted_ties
            if predicted_ties > 0:
                sentences_with_ties += 1
            pairs_overall += pairs
            
        
        
        
        tau = 1.00 * (concordant - discordant) / (concordant + discordant)
        prob = kendall_tau_prob(tau, valid_pairs)
        
        avg_seg_tau = np.average(segtaus)               
        avg_seg_prob = np.product(segprobs)
        
        predicted_ties_avg = 100.00*predicted_ties / pairs_overall
        sentence_ties_avg = 100.00*sentences_with_ties / len(self.parallelsentences)
        
        stats = {'tau': tau,
                 'prob': prob,
                 'avg_seg_tau': avg_seg_tau,
                 'avg_seg_prob': avg_seg_prob,
                 'concordant': concordant,
                 'discordant': discordant,
                 'valid_pairs': valid_pairs,
                 'all_pairs': pairs_overall,
                 'original_ties': original_ties_overall,
                 'predicted_ties': predicted_ties_overall,
                 'predicted_ties_per': predicted_ties_avg,
                 'sentence_ties': sentences_with_ties,
                 'sentence_ties_per' : sentence_ties_avg
                 
                 }
        
        stats = dict([("{}{}{}".format(prefix, key, suffix),value) for key,value in stats.iteritems()])
        
        return stats
    
    
    
    def get_kendall_tau_b(self, predicted_rank_name, original_rank_name):
        """
        Calculates Kendall tau beta of predicted vs human ranking according to the Knight (1966) 
        [scipy implementation] taking account of ties    
        @param predicted_rank_name: the name of the attribute containing the predicted rank
        @type predicted_rank_name: str 
        @param original_rank_name: the name of the attribute containing the human rank
        @type original_rank_name: str
        @return: the Kendall tau score and the probability for the null hypothesis of X and Y being independent
        @rtype: tuple(float, float)
        """
        from scipy.stats import kendalltau
        from numpy import isnan

        segment_tau = 0.00
        segment_pi = 1.00
        for parallelsentence in self.parallelsentences:
            predicted_rank_vector = parallelsentence.get_target_attribute_values(predicted_rank_name)
            original_rank_vector = parallelsentence.get_target_attribute_values(original_rank_name)
            
            logging.debug("[{0}]".format(" , ".join(predicted_rank_vector)))
            logging.debug("[{0}]".format(" , ".join(original_rank_vector)))
            
            #if had this denominator error, just provide the result of smoothing
            try:
                tau, pi = kendalltau(original_rank_vector, predicted_rank_vector)
            except TypeError:
                tau = kendalltau(original_rank_vector, predicted_rank_vector)
                pi = 1.00
                sys.stderr.write("==============\nScipy gave an erroneous tau = {}\n==============".format(tau))
            if isnan(tau) or isnan(pi):
                tau = 0.00
                pi = 1.00

            segment_tau += tau
            segment_pi *= pi
            logging.debug("tau = {}".format(tau))
        
        avg_tau = 1.00 * segment_tau / len(self.parallelsentences)
        
        
        logging.debug("Avg tau:  segment_tau / len(self.parallelsentences) \n= {0} / {1}  \n= {2}".format(segment_tau, len(self.parallelsentences), avg_tau))
        return avg_tau, segment_pi
    

def regenerate_tau():
    """
    Test script which should be run particularly from with the separate app folders, 
    in order to reproduce results without re-executing the app script
    """
    
    from dataprocessor.input.jcmlreader import JcmlReader
    d = JcmlReader("testset.reconstructed.hard.jcml").get_dataset()
    scoringset = Scoring(d)
    print scoringset.get_kendall_tau("rank_hard", "rank")
            
            
        
             
if __name__ == '__main__':
    #get_metrics_scores
    pass
        
        
    
        

