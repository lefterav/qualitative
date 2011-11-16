'''
Created on Nov 16, 2011

@author: jogin
'''

import sys
sys.path.append("/home/lupo01")

from featuregenerator.levenshtein.levenshtein import levenshtein_tok


class OOLinkage():
    """
    This script compares sentences from Open Office 2010 with sentences from Open Office 2011 (OpenOffice3) according to Levenshtein distance.
    """
    def __init__(self, oldOOSnts, newOOSnts, newOOLinks='', oldOOLinks=''):
        """
        @param: oldOOSnts: old Open Office file with aligned sentences
        @type: string
        @param: newOOSnts: new Open Office file with aligned sentences
        @type: string
        @param: newOOLinks: new Open Office file with source links of aligned sentences
        @type: string
        @param: oldOOLinks: filename for saving links of sentence and source
        @type: string
        """
        f = open(oldOOSnts)
        oldSntsStr = f.read()
        f.close()
        
        f = open(newOOSnts)
        newSntsStr = f.read()
        f.close()

        oldSnts = oldSntsStr.split('\n')
        newSnts = newSntsStr.split('\n')

        # Levenshtein distance 4 or less:
        # 9, 14, 15, 20
        b = 0
        f = open('log.txt','w')
        for oldSnt in oldSnts:
            a = 0
            b += 1
            if b < 42: continue
            print b
            for newSnt in newSnts:
                if levenshtein_tok(oldSnt, newSnt) > 4: continue
                else:
                    
                    a += 1
                    print str(b), '-', str(a), ':'
                    print 'Ref:\n', oldSnt
                    print 'Candidate:\n', newSnt
                    print 'Levenshtein:', str(levenshtein_tok(oldSnt, newSnt)), '\n'
                    f.write(str(b)+' - '+str(a)+':')
                    f.write('Ref:\n'+oldSnt)
                    f.write('Candidate:\n'+newSnt)
                    f.write('Levenshtein: '+str(levenshtein_tok(oldSnt, newSnt))+'\n')
            if b > 60: break
        f.close()


# '/share/taraxu/data/KDE4/aligned/cs-en_src.txt', '/share/taraxu/data/KDE4/aligned/cs-en_tgt.txt', 100, '/share/taraxu/data/KDE4/aligned/
OOLinkage('/media/DATA/Arbeit/DFKI/111102_OpenOffice/oolinkage/esde_src.c40.detok.txt', '/media/DATA/Arbeit/DFKI/111102_OpenOffice/oolinkage/de-es_tgt_detok.txt')

#'/home/lupo01/oo/selected/openoffice.de-en.sel104.detok.de', '/home/lupo01/oo/aligned/esde_src_detok.txt', '/share/taraxu/data/OpenOffice3/aligned/de-en_GB_src_links.txt', '/home/lupo01/oo/selected/openoffice.de-en.sel104.detok.de_links.txt'

#'/home/lupo01/oo/selected/openoffice.de-en.sel104.detok.de', '/share/taraxu/data/OpenOffice3/aligned/de-en_GB_src_detok.txt', '/share/taraxu/data/OpenOffice3/aligned/de-en_GB_src_links.txt', '/home/lupo01/oo/selected/openoffice.de-en.sel104.detok.de_links.txt'

#'/home/lupo01/oo/selected/esde_tgt.c40.detok.txt', '/share/taraxu/data/OpenOffice3/aligned/de-es_src_detok.txt', '/share/taraxu/data/OpenOffice3/aligned/de-es_src_links.txt', '/home/lupo01/oo/selected/esde_tgt.c40.detok_links.txt'

#'/home/lupo01/oo/selected/esde_src.c40.detok.txt', '/share/taraxu/data/OpenOffice3/aligned/de-es_tgt_detok.txt', '/share/taraxu/data/OpenOffice3/aligned/de-es_tgt_links.txt', '/home/lupo01/oo/selected/esde_src.c40.detok_links.txt'
