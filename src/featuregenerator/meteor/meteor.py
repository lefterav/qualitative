'''
Created on 15 Jun 2012

@author: elav01
'''

from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayClient
from py4j.java_gateway import java_import
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator

class MeteorGenerator(LanguageFeatureGenerator):
    '''
    classdocs
    '''


#    def __init__(self, lang, classpath):
    def __init__(self, lang, gateway):
        '''
        Constructor
        '''
        self.lang = lang
    
    
        meteor_view = gateway.new_jvm_view()
        java_import(meteor_view, 'edu.cmu.meteor.scorer.*')
        java_import(meteor_view, 'edu.cmu.meteor.util.*')
        
#        import edu.cmu.meteor.scorer.MeteorScorer; 
#        import edu.cmu.meteor.scorer.MeteorConfiguration;
#        import edu.cmu.meteor.scorer.MeteorStats;
#        import edu.cmu.meteor.util.Constants;
#        import edu.cmu.meteor.util.Normalizer;
#        import edu.cmu.meteor.util.SGMData;

        
        config = meteor_view.MeteorConfiguration();
        config.setLanguage(lang);
        self.scorer = meteor_view.MeteorScorer(config)
        
        
    
    def score(self, target, references):
        stats = self.scorer.getMeteorStats(target, references);
        
        return {'meteor_precision' : '{:.4}'.format(stats.precision), 
                'meteor_recall' : '{:.4}'.format(stats.recall), 
                'meteor_fragPenalty' : '{:.4}'.format(stats.fragPenalty),  
                'meteor_score' : '{:.4}'.format(stats.score)}
    


class CrossMeteorGenerator(MeteorGenerator):
    
    def get_features_tgt(self, translation, parallelsentence):
        current_system_name = translation.get_attribute("system")
        alltranslations = dict([(t.get_attribute("system"), t.get_string()) for t in parallelsentence.get_translations()])
        del(alltranslations[current_system_name])
        references = alltranslations.values()
        stats = self.score(translation.get_string(), references)
        return stats
