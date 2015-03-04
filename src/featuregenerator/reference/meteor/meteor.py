'''
Calculate translation METEOR scores against reference (MeteorGenerator) and against competitive translations (CrossMeteorGenerator)

Created on 15 Jun 2012
@author: Eleftherios Avramidis
'''

from py4j.java_gateway import java_import
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator

class MeteorGenerator(LanguageFeatureGenerator):
    '''
    Uses an existing JavaGateway (Py4j) in order to perform METEOR scoring and
    serve that as features. This Feature Generator overwrites the inherited get_features_tgt 
    function for scoring target vs. the embedded reference translation of the 
    ParallelSentence. See L{CrossMeteorGenerator} for target cross-scoring.
    @ivar lang: The language code for the proper initialization of the included 
    language-dependent tool
    @type lang: string
    @ivar gateway: An already initialized Py4j java gateway
    @type gateway: py4j.java_gateway.JavaGateway
    @ival scorer: The initialized object of the MeteorScorer
    @type scorer: edu.cmu.meteor.scorer.MeteorScorer
    '''
    __name__ = "Meteor"

    def __init__(self, lang, gateway):
        '''
        Constructor
        @param lang: The language code for the proper initialization of this language-dependent tool
        @type lang: string
        @param gateway: An already initialized Py4j java gateway
        @type gateway: py4j.java_gateway.JavaGateway
        '''
        self.lang = lang
        #self.jvm = JVM(java_classpath)
        #socket_no = self.jvm.socket_no
        #gatewayclient = GatewayClient('localhost', socket_no)
        #gateway = JavaGateway(gatewayclient, auto_convert=True, auto_field=True)
        #sys.stderr.write("Initialized local Java gateway with pid {} in socket {}\n".format(self.jvm.pid, socket_no))
    
        self.meteor_view = gateway.new_jvm_view()
        #import necessary java packages from meteor jar
        java_import(self.meteor_view, 'edu.cmu.meteor.scorer.*')
        java_import(self.meteor_view, 'edu.cmu.meteor.util.*')
#        java_import(self.meteor_view, '')
        
        #pass the language setting into the meteor configuration object
        config = self.meteor_view.MeteorConfiguration();
        config.setLanguage(lang);
        #initialize object with the given config
        self.scorer = self.meteor_view.MeteorScorer(config)

    
    def get_features_tgt(self, translation, parallelsentence):
        try:
            references = [parallelsentence.get_reference().get_string()]
            stats = self.score_sentence(translation.get_string(), references)
            stats = dict([("ref-{}".format(k),v) for k, v in stats.iteritems()])
            return stats
        except:
            return {}

    def score(self, target, references):
        return self.score_sentence(target, references)

    def score_sentence(self, target, references):

        '''
        Score using the METEOR metric given one translated sentence, given a list of reference translations
        @param target: The text of the (machine-generated) translation
        @type target: string
        @param references: A list of the reference translations, text-only
        @type references: [string, ...]
        @return: A dictionary of the various METEOR scoring results, namely precision, recall, fragPenalty and score
        @rtype: {string: string}
        '''
        stats = self.scorer.getMeteorStats(target, references);
        
        return {'meteor_precision' : '{:.4}'.format(stats.precision), 
                'meteor_recall' : '{:.4}'.format(stats.recall), 
                'meteor_fragPenalty' : '{:.4}'.format(stats.fragPenalty),  
                'meteor_score' : '{:.4}'.format(stats.score)}
    
    def analytic_score_sentences(self, sentence_tuples):    
        """
        Score many sentences using METEOR and return all basic scores. 
        @param sentence_tuples: a list of tuples generated out of the translated sentences. Each
        tuple should contain one translated sentence and its list of references.
        @type sentence_tuples: [tuple(str(translation), [str(reference), ...]), ...] 
        @return: a dictionary containing METEOR scores, name and value
        @rtype: dict(score_name,score_value)
        """    
        aggregated_stats = self.meteor_view.MeteorStats()
        
        for target, references in sentence_tuples:
            stats = self.scorer.getMeteorStats(target, references)
            aggregated_stats.addStats(stats)
            
        self.scorer.computeMetrics(aggregated_stats)
        return {'meteor_precision' : '{:.4}'.format(aggregated_stats.precision), 
                'meteor_recall' : '{:.4}'.format(aggregated_stats.recall), 
                'meteor_fragPenalty' : '{:.4}'.format(aggregated_stats.fragPenalty),  
                'meteor_score' : '{:.4}'.format(aggregated_stats.score)}
    
    def score_sentences(self, sentence_tuples):
        """
        Score many sentences using METEOR metrics and return a float for the many score
        @param sentence_tuples: a list of tuples generated out of the translated sentences. Each
        tuple should contain one translated sentence and its list of references.
        @type sentence_tuples: [tuple(str(translation), [str(reference), ...]), ...] 
        @return: the basic score float value
        @rtype: float
        """ 
        return float(self.analytic_score_sentences(sentence_tuples)['meteor_score'])


class CrossMeteorGenerator(MeteorGenerator):
    '''
    Overwrites the feature generation function, by allowing the provided target sentence
    (i.e. translation) to be scored against the translations provided by the other systems
    embedded in this Parallel Sentence.
    '''
    
    def get_features_tgt(self, translation, parallelsentence):
        current_system_name = translation.get_attribute("system")
        alltranslations = dict([(t.get_attribute("system"), t.get_string()) for t in parallelsentence.get_translations()])
        del(alltranslations[current_system_name])
        references = alltranslations.values()
        stats = self.score_sentence(translation.get_string(), references)
        stats = dict([("cross-{}".format(k),v) for k, v in stats.iteritems()])
        return stats





    
    
