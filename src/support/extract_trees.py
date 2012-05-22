# -*- coding: utf-8 -*-
# copyright DFKI GmbH @ TaraXUe project

import sys
import codecs

LANGUAGES = {
             'Spanish' : 'es',
             'English' : 'en',
             'Czech' : 'cz',
             'German' : 'de',
             'French' : 'fr'
             }

def extract_source(path, language, sentence_index):
    translations = list(enumerate(codecs.open('%s/newssyscombtest2010.%s' %
                               (path, language), 'r', 'utf-8')))
    result = ''
    for (index, sentence) in translations:
        if index == sentence_index:
            result = sentence
            break
    return result

def extract_trees(lucy, source, direction):
    textin = list(codecs.open('%s/%s/newstest2010.%s' %
                       (lucy, direction, direction[:2]), 'r', 'utf-8'))
    textout = list(codecs.open('%s/%s/lucy.%s.output' %
                       (lucy, direction, direction), 'r', 'utf-8'))
    ana_trees = list(codecs.open('%s/%s/temp/lucy-analysis.aligned' %
                                 (lucy, direction), 'r', 'utf-8'))
    tra_trees = list(codecs.open('%s/%s/temp/lucy-transfer.aligned' %
                                 (lucy, direction), 'r', 'utf-8'))
    result = (False, '', '')
    index = -1
    for line in textin:
        if source.strip() == line.strip():
            index = textin.index(line)
            break
    phrasal = False
    if index != -1:
        if 'PHR-S' in tra_trees[index]:
            phrasal = True
        result = (phrasal, textout[index], ana_trees[index])
    return result

def create_trees(judgments, lucypath, sourcepath):
    for line in judgments:
        fields = line.split(',')
        src = LANGUAGES[fields[0]]
        tgt = LANGUAGES[fields[1]]
        dir = src + '-' + tgt
        index = int(fields[2])
        if 'dfki' in fields:
            pos = fields.index('dfki')
        if pos == 7:
            rank = fields[16]
        elif pos == 9:
            rank = fields[17]
        elif pos == 11:
            rank = fields[18]
        elif pos == 13:
            rank = fields[19]
        elif pos == 15:
            rank = fields[20]

        source = extract_source(sourcepath, src, index)
        (phrasal, sentence, tree) = extract_trees(lucypath, source, dir)
        tree = tree.replace('\t', ' ')
        out = codecs.open('%s.trees' % dir, 'a', 'utf-8')
        out.write('%s\t%s\t%s\t%s' % (rank.strip(), phrasal, sentence.strip(), tree))

    out.close()
    return None

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print 'USAGE: %s LUCYPATH SOURCEPATH JUDGMENTS.CSV' % sys.argv[0]
        print '\tlucypath = path to folder with lucy trees'
        print '\tsourcepath = path to folder with evaluation raw data'
    else:
        lucypath = sys.argv[1]
        sourcepath = sys.argv[2]
        judgments = codecs.open(sys.argv[3], 'r', 'utf-8')
        create_trees(judgments, lucypath, sourcepath)
