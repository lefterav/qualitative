'''
Created on 18 Oct 2011

@author: Elefherios Avramidis
'''

from dataprocessor.input.jcmlreader import JcmlReader

def _add_rank(dic, system):
    if dic.has_key(system):
        dic[system] += 1
    else:
        dic[system] = 1
    return dic

if __name__ == '__main__':
    parallelsentences = JcmlReader("/home/elav01/taraxu_data/ml4hmt/news-test2008-test.es-en.withlang.if.jcml").get_parallelsentences()
    bleuoutput_file = open("/home/elav01/taraxu_data/ml4hmt/tst/sentence-bleu.txt", 'w')
    levoutput_file = open("/home/elav01/taraxu_data/ml4hmt/tst/sentence-lev.txt", 'w')
    ref_file = open("/home/elav01/taraxu_data/ml4hmt/tst/ref.txt", 'w')
    systems = 5
    system_file = {}
    for system in range(systems):
        system_name = "t%s" % str(system + 1)
        system_file[system_name] = open("/home/elav01/taraxu_data/ml4hmt/tst/output-%s.txt" % system_name, 'w')
    
    
    bleu_rankvector = {}
    lev_rankvector = {}
    for parallelsentence in parallelsentences:
        ref_file.write(parallelsentence.get_reference().get_string())
        ref_file.write("\n")
        for tgt in parallelsentence.get_translations():
            system_name = tgt.get_attribute("system")
            bleu = int(tgt.get_attribute("bleu-rank"))
            if bleu == 1:
                bleu_rankvector = _add_rank(bleu_rankvector, system_name)
                bleuoutput_file.write(tgt.get_string())
                bleuoutput_file.write("\n")
                break
                        
        for tgt in parallelsentence.get_translations():
            system_name = tgt.get_attribute("system")
            lev = int(tgt.get_attribute("lev-rank"))
            if lev == 1:
                lev_rankvector = _add_rank(lev_rankvector, system_name)
                levoutput_file.write(tgt.get_string())
                levoutput_file.write("\n")
                break
        
        for tgt in parallelsentence.get_translations():
            system_name = tgt.get_attribute("system")
            system_file[system_name].write(tgt.get_string())
            system_file[system_name].write("\n")
    
    for system in bleu_rankvector:
        print system , "&" , bleu_rankvector[system], "&" , round(100.0 * bleu_rankvector[system] / len(parallelsentences), 2), "\% //"
    
    print
    
    for system in bleu_rankvector:
        print system, "&" , lev_rankvector[system], "&" , round(100.0 * lev_rankvector[system] / len(parallelsentences), 2), "\% //"
    
    
    bleuoutput_file.close()
    levoutput_file.close()
    ref_file.close()
    for system_name in system_file:
        system_file[system_name].close()
    
        
        
        
    