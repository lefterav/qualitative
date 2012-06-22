'''
Created on 15 Jun 2012

@author: elav01
'''

from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayClient
from py4j.java_gateway import java_import
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
from util.jvm import JVM
import sys

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

    def __init__(self, lang, java_classpath, dir_path):
        '''
        Constructor
        @param lang: The language code for the proper initialization of this language-dependent tool
        @type lang: string
        @param gateway: An already initialized Py4j java gateway
        @type gateway: py4j.java_gateway.JavaGateway
        '''
        self.lang = lang
        self.jvm = JVM(java_classpath, dir_path)
        socket_no = self.jvm.socket_no
        gatewayclient = GatewayClient('localhost', socket_no)
        gateway = JavaGateway(gatewayclient, auto_convert=True, auto_field=True)
        sys.stderr.write("Initialized local Java gateway with pid {} in socket {}\n".format(self.jvm.pid, socket_no))
    
        meteor_view = gateway.new_jvm_view()
        #import necessary java packages from meteor jar
        java_import(meteor_view, 'edu.cmu.meteor.scorer.*')
        java_import(meteor_view, 'edu.cmu.meteor.util.*')
        
        #pass the language setting into the meteor configuration object
        config = meteor_view.MeteorConfiguration();
        config.setLanguage(lang);
        #initialize object with the given config
        self.scorer = meteor_view.MeteorScorer(config)

    
    def get_features_tgt(self, translation, parallelsentence):
        references = [parallelsentence.get_reference().get_string()]
        stats = self.score(translation.get_string(), references)
        return stats


    def score(self, target, references):
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
        stats = self.score(translation.get_string(), references)
        return stats





    
    