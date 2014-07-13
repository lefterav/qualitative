'''
Created on 25 Mar 2014
@author: Eleftherios Avramidis
'''
import sys
import yaml
from dataprocessor.sax.utils import join_filter_jcml, CEJcmlReader, join_jcml
from dataprocessor.input.jcmlreader import JcmlReader
from ml.lib.scikit.scikit import SkRegressor, TerRegressor, dataset_to_instances
import logging as log
import numpy as np
from numpy import array
from expsuite import PyExperimentSuite
import time

#todo: this should be read from config file (or expsuite)
cfg_path = "/home/elav01/workspace/qualitative/src/app/hter/config/svr.cfg"
class_name = "ter_ter"
desired_parallel_attributes = []
desired_source_attributes = []

N_FOLDS=10

TEST_FOLDS = [array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
       17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
       34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
       51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67,
       68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84,
       85, 86, 87, 88, 89]), array([ 90,  91,  92,  93,  94,  95,  96,  97,  98,  99, 100, 101, 102,
       103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115,
       116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128,
       129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141,
       142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154,
       155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167,
       168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179]), array([180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192,
       193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205,
       206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218,
       219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231,
       232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244,
       245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257,
       258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269]), array([270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282,
       283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295,
       296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308,
       309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321,
       322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334,
       335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347,
       348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359]), array([360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372,
       373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385,
       386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398,
       399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411,
       412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424,
       425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437,
       438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449]), array([450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462,
       463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475,
       476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488,
       489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501,
       502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514,
       515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527,
       528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539]), array([540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552,
       553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565,
       566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578,
       579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591,
       592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604,
       605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617,
       618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628]), array([629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641,
       642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654,
       655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667,
       668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680,
       681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693,
       694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706,
       707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717]), array([718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730,
       731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743,
       744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756,
       757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769,
       770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782,
       783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795,
       796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806]), array([807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819,
       820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832,
       833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845,
       846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858,
       859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871,
       872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884,
       885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895])]

ter_class_names = ["ter_deletions","ter_insertions", "ter_substitutions","ter_shifts"]



#"berkeley-best-parse-confidence"
desired_target_attributes = ["l_tokens","berkeley-n","berkley-loglikelihood","l_avgchars","l_chars","lm_bi-prob","lm_bi-prob_avg","lm_bi-prob_high","lm_bi-prob_low","lm_bi-prob_low_pos_avg","lm_bi-prob_low_pos_std","lm_bi-prob_std","lm_prob","lm_tri-prob","lm_tri-prob_avg","lm_tri-prob_high","lm_tri-prob_low","lm_tri-prob_low_pos_avg","lm_tri-prob_low_pos_std","lm_tri-prob_std","lm_uni-prob","lm_uni-prob_avg","lm_uni-prob_high","lm_uni-prob_low","lm_uni-prob_low_pos_avg","lm_uni-prob_low_pos_std","lm_uni-prob_std","lm_unk","lm_unk_len","lm_unk_pos_abs_avg","lm_unk_pos_abs_max","lm_unk_pos_abs_min","lm_unk_pos_abs_std","lm_unk_pos_rel_avg","lm_unk_pos_rel_max","lm_unk_pos_rel_min","lm_unk_pos_rel_std","lt_COMMA_PARENTHESIS_WHITESPACE","lt_DET_NOM_SING","lt_EL_FINAL","lt_ESTAR_CLARO_DE_QUE","lt_NOM_ADJ_FEM","lt_NOM_ADJ_MASC","lt_NOM_ADJ_PLURAL","lt_NOM_ADJ_SINGULAR","lt_PP_V_PLURAL","lt_PP_V_SINGULAR","lt_SE_FINAL","lt_UNPAIRED_BRACKETS","lt_UPPERCASE_SENTENCE_START","lt_VERBO_DE_QUE","lt_WORD_REPEAT_RULE","lt_Y_E","lt_errors","lt_errors_chars","lt_lt_COMMA_PARENTHESIS_WHITESPACE_chars","lt_lt_DET_NOM_SING_chars","lt_lt_EL_FINAL_chars","lt_lt_ESTAR_CLARO_DE_QUE_chars","lt_lt_NOM_ADJ_FEM_chars","lt_lt_NOM_ADJ_MASC_chars","lt_lt_NOM_ADJ_PLURAL_chars","lt_lt_NOM_ADJ_SINGULAR_chars","lt_lt_PP_V_PLURAL_chars","lt_lt_PP_V_SINGULAR_chars","lt_lt_SE_FINAL_chars","lt_lt_UNPAIRED_BRACKETS_chars","lt_lt_UPPERCASE_SENTENCE_START_chars","lt_lt_VERBO_DE_QUE_chars","lt_lt_WORD_REPEAT_RULE_chars","lt_lt_Y_E_chars","parse-CC","parse-CC-pos-avg","parse-CC-pos-std","parse-DT","parse-DT-pos-avg","parse-DT-pos-std","parse-JJ","parse-JJ-pos-avg","parse-JJ-pos-std","parse-NN","parse-NN-pos-avg","parse-NN-pos-std","parse-NP","parse-NP-pos-avg","parse-NP-pos-std","parse-PP","parse-PP-pos-avg","parse-PP-pos-std","parse-S","parse-S-pos-avg","parse-S-pos-std","parse-VB","parse-VB-pos-avg","parse-VB-pos-std","parse-VP","parse-VP-pos-avg","parse-VP-pos-std","parse-comma","parse-comma-pos-avg","parse-comma-pos-std","parse-dot","parse-dot-pos-avg","parse-dot-pos-std","qb_1001","qb_1002","qb_1006","qb_1009","qb_1012","qb_1015","qb_1022","qb_1036","qb_1046","qb_1049","qb_1050","qb_1053","qb_1054","qb_1057","qb_1058","qb_1074","qb_1075"]
#desired_target_attributes = ["l_tokens","q_1022_1","q_1012_1","q_1015_1","q_1001_1","q_1002_1","q_1006_1","q_1036_1","q_1009_1","q_1057_1","q_1054_1","q_1053_1","q_1050_1","q_1049_1"]
#"q_1075_1","q_1074_1",,"q_1046_1"
#["qb_1022","qb_1012","qb_1015","qb_1001","qb_1002","qb_1006","qb_1036","qb_1009","qb_1057","qb_1054","qb_1053","qb_1050","qb_1049","qb_1075","qb_1074","qb_1046"]


def filter_sentence_ter(parallelsentence, **kwargs):
    """
    Calback which returns true, if given parallelsentence has less than 
    specific number of specific TER edits
    @keyword ter_deletions: maximum number of allowed deletions
    @keyword ter_insertions: maximum number of allowed insertions
    @keyword ter_substitutions: maximum number of allowed substitutions
    @keyword ter_shifts: maximum number of allowed shifts
    @keyword ter_edits: maximum number of allowed edits
    @return: True if all specified filters hold
    @rtype: boolean
    """
    atts = parallelsentence.get_translations()[0].get_attributes()
    return (float(atts["ter_deletions"]) <= float(kwargs.setdefault("filter_deletions", "Inf"))
            and float(atts["ter_insertions"]) <= float(kwargs.setdefault("filter_insertions", "Inf"))
            and float(atts["ter_substitutions"]) <= float(kwargs.setdefault("filter_substitutions", "Inf"))
            and float(atts["ter_shifts"]) <= float(kwargs.setdefault("filter_shifts", "Inf"))
            and float(atts["ter_edits"]) <= float(kwargs.setdefault("filter_edits", "Inf"))
           )
    
    

def train_regressor(config, dataset, class_name, desired_parallel_attributes, desired_source_attributes, desired_target_attributes):
    regressor = SkRegressor(config)
    log.info("Loading data")
    regressor.load_training_dataset(dataset, class_name, desired_parallel_attributes, desired_source_attributes, desired_target_attributes, [], False)
    regressor.set_learning_method()
    return regressor
    
def train_ter_separately(config, dataset, class_name, desired_parallel_attributes, desired_source_attributes, desired_target_attributes):
    regressors = []
    dummy, tergold = dataset_to_instances(dataset, class_name)
    #print "TERgold = " , tergold
    for class_name in ter_class_names:
        log.info("Training regressor for {}".format(class_name))
        regressor = train_regressor(config, dataset, class_name, desired_parallel_attributes, desired_source_attributes, desired_target_attributes)
        regressors.append(regressor)
    return TerRegressor(config, regressors, tergold)


    

    
#    scores = parallel(
#        delayed(ter_cross_validate_fold)([clone(estimator) for estimator in estimators], 
#                                         X, y, scorer, train, test, verbose, fit_params)
#    for train, test in cv)    
    


class HTERSuite(PyExperimentSuite):
    def reset(self, params, rep):
        self.learner_configfile = params["learner_configfile"].format(**params)
        self.source_attributes = params["{}_source".format(params["att"])].split(",")
        self.target_attributes = params["{}_target".format(params["att"])].split(",")
        self.general_attributes = params["{}_general".format(params["att"])].split(",")
        self.class_name = params["class_name"]
        self.training_sets = params["training_sets"].format(**params).split(',')
        try:
            self.training_sets_tofilter = params["training_sets_tofilter"].format(**params).split(',')
        except:
            self.training_sets_tofilter = None
        self.filters = dict([(key, value) for key, value in params.iteritems() if key.startswith("filter_")])
        self.roundup = params["roundup"]
        self.mode = params["mode"]
        
        #self.existing_folds = eval(params["test_folds"])
        self.existing_folds = TEST_FOLDS
        #self.n_folds = eval(params["n_folds"])
        self.n_folds = N_FOLDS
    
    
    def iterate(self, params, rep, n):
        
        ret = {}
        #logging
        log.basicConfig(level=log.INFO)
        
        if self.training_sets_tofilter:
            additional_training_filename = "training.additional.filtered.jcml"
            
            log.info("Filtering addiitional files")                
            ret["used_sentences"], ret["total_sentences"] = join_filter_jcml(self.training_sets_tofilter, additional_training_filename, filter_sentence_ter, **self.filters)
            self.training_sets.append(additional_training_filename)
    
        #load and join filenames
        log.info("Creating joined file")        
        log.info("Input filenames: {}".format(self.training_sets))
        basic_xml_filename = "train.jcml"
        join_jcml(self.training_sets, basic_xml_filename)
            
        dataset = CEJcmlReader(basic_xml_filename, all_general=True, all_target=True)
    
        # open the config file for scikit
        config = None
        with open(self.learner_configfile, "r") as cfg_file:
            config = yaml.load(cfg_file.read())
        
        
        #initialize the generic regressor
        if self.mode=="single":
            regressor = SkRegressor(config)
            log.info("Loading data")
            regressor.load_training_dataset(dataset, class_name, 
                                            self.general_attributes, 
                                            self.source_attributes, 
                                            self.target_attributes)
            regressor.set_learning_method()
            log.info("Single regressor: Performing cross validation")
            scores = regressor.cross_validate_start(cv=self.n_folds, fixed_folds=self.existing_folds)
        else: 
            log.info("Combined regressors: Training")        
            ter_regressor = train_ter_separately(config, dataset, class_name, 
                                                self.general_attributes, 
                                                self.source_attributes, 
                                                self.target_attributes)
            log.info("Combined regressors: Performing cross validation")        
            scores = ter_regressor.cross_validate_start(cv=self.n_folds, 
                                                        fixed_folds=self.existing_folds,
                                                        roundup = self.roundup)
            
        ret["mae_avg"] = "{:.3f}".format(np.average(scores))
        ret["mae_std"] = "{:.3f}".format(np.std(scores))
        ret.update(dict([("mae_fold_{}".format(i-2), "{:.3f}".format(value)) for i, value in enumerate(scores[2:])])) 
        log.info("[{}]\t{:.3f}\t{:.3f}\t[{}]".format(self.mode, 
                                                     np.average(scores), 
                                                     np.std(scores),
                                                     ",".join(["{:.3f}".format(s) for s in scores]))
                                                     )
        
        
        log.info("Done! Go check the results...")
        log.info(time.ctime())
        return ret


if __name__ == '__main__':
    mysuite = HTERSuite();
    mysuite.start()
    
