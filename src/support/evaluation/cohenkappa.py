'''
Created on Jul 21, 2011

@author: jogin
'''

from io_utils.input.rankreader import RankReader



class CohenKappa(object):
    
    def get_cohen_kappa(self, system_names, rankingFile1, rankingFile2):
        """
        This function compares ranking difference between 2 ranking files and
        count from that a coefficient Cohen's kappa. Further information about
        this can be found at: http://en.wikipedia.org/wiki/Cohen%27s_kappa
        @param systems: names of 2 systems to be compared
        @type systems: tuple of strings
        @param rankingFile1: xml ranking file 1
        @type rankingFile1: string
        @param rankingFile2: xml ranking file 2
        @type rankingFile2: string
        @return cohen_kappa: computed Cohen's kappa coefficient
        @type cohen_kappa: float
        """
        psList1 = RankReader(rankingFile1).get_parallelsentences()
        psList2 = RankReader(rankingFile2).get_parallelsentences()
    
        equalBoth = 0
        betterBoth = 0
        worseBoth = 0
        equal1 = 0
        better1 = 0
        worse1 = 0
        equal2 = 0
        better2 = 0
        worse2 = 0
        
        system_pairs = self.__get_pairs__(system_names)
        print system_pairs
        
        for ps1 in psList1:
            for ps2 in psList2:
                for systems in system_pairs:
                    if ps1.get_attribute('sentence-id') == ps2.get_attribute('sentence-id'):
                        pairwisePS1 = ps1.get_pairwise_parallelsentences()
                        pairwisePS2 = ps2.get_pairwise_parallelsentences()
        
                        pps1 = pairwisePS1.get_pairwise_parallelsentence(systems)
                        rankPS11 = pps1.get_translations()[0].get_attribute('rank')
                        rankPS12 = pps1.get_translations()[1].get_attribute('rank')
                        pps2 = pairwisePS2.get_pairwise_parallelsentence(systems)
                        rankPS21 = pps2.get_translations()[0].get_attribute('rank')
                        rankPS22 = pps2.get_translations()[1].get_attribute('rank')
        
                        if rankPS11 == rankPS12 and rankPS21 == rankPS22:
                            equalBoth += 1             
                        elif rankPS11 > rankPS12 and rankPS21 > rankPS22:
                            betterBoth += 1
                        elif rankPS11 < rankPS12 and rankPS21 < rankPS22:
                            worseBoth += 1
        
                        if rankPS11 == rankPS12:
                            equal1 += 1
                        elif rankPS11 > rankPS12:
                            better1 += 1
                        else:      
                            worse1 += 1
        
                        if rankPS21 == rankPS22:
                            equal2 += 1
                        elif rankPS21 > rankPS22:
                            better2 += 1
                        else:
                            worse2 += 1        
                        break
        
        match = equalBoth + betterBoth + worseBoth
        total = equal1 + better1 + worse1
        prA = float(match)/total
        prE = (float(equal1)/total)*(float(equal2)/total) + \
               (float(better1)/total)*(float(better2)/total) + \
               (float(worse1)/total)*(float(worse2)/total)
    
        cohen_kappa = (prA - prE)/(1 - prE)
        return cohen_kappa
    
    def __get_pairs__(self, items):
        """
        Returns a list of tuples, of all pairwise combinations among the items of the list
        """
        return [(items[i],items[j]) for i in range(len(items)) for j in range(i+1, len(items))]

system_names = [  "google", "moses", "lucy"]
print CohenKappa().get_cohen_kappa(system_names, "/home/lefterav/taraxu_data/r1/results/6-1-WMT08-de-en-ranking.xml", "/home/lefterav/taraxu_data/r1/results/19-1-WMT08-de-en-ranking.xml")