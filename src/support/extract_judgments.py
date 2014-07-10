# -*- coding: utf-8 -*-

import sys
import codecs

LANGUAGES = {
             'Spanish' : 'es',
             'English' : 'en',
             'Czech' : 'cz',
             'German' : 'de',
             'French' : 'fr'
             }

def extract_sentence(path, system, direction, sentence_index):
    result = ''
    if system != '_ref':
        translations = list(enumerate(codecs.open('%s/submissions/newssyscombtest2010.%s.%s' %
                               (path, direction, system), 'r', 'utf-8')))
        for (index, sentence) in translations:
            if index == sentence_index:
                result = sentence
                break
    else:
        result = extract_ref(path, direction[-2:], sentence_index)

    return result

def extract_sourceref(path, language, sentence_index):
    translations = list(enumerate(codecs.open('%s/newssyscombtest2010.%s' %
                               (path, language), 'r', 'utf-8')))
    result = ''
    for (index, sentence) in translations:
        if index == sentence_index:
            result = sentence
            break
    return result

def extract_ref(path, language, sentence_index):
    translations = list(enumerate(codecs.open('%s/newssyscombtest2010.%s' %
                               (path, language), 'r', 'utf-8')))
    result = ''
    for (index, sentence) in translations:
        if index == sentence_index:
            result = sentence
            break
    return result

def write_rankings(source, rankings, file_gt, file_lt, file_eq):
    rank_g = 0
    rank_d = 0
    for (rank, sys, sent) in rankings:
        if sys == 'dfki':
	    rank_d = int(rank)
	elif sys == 'onlineB':
	    rank_g = int(rank)
    
    file = None
    if rank_g < rank_d:
	file = file_gt
    elif rank_g == rank_d:
	file = file_eq
    else:
	file = file_lt

    file.write('SOURCE:\t%s\n' % source)
    for (rank, sys, sent) in rankings:
        if sys == 'dfki':
            sys = '***dfki***'
	elif sys == 'onlineB':
	    sys = '***google***'
        file.write('%s:\t%s\t->\t %s\n' % (rank.strip(), sys, sent))
    return None

def create_evaluation(judgments, path):

    out_gt = codecs.open('evaluations_gt', 'w', 'utf-8')
    out_lt = codecs.open('evaluations_lt', 'w', 'utf-8')
    out_eq = codecs.open('evaluations_eq', 'w', 'utf-8')
    for line in judgments:
        fields = line.split(',')
        src = LANGUAGES[fields[0]]
        tgt = LANGUAGES[fields[1]]
        dir = src + '-' + tgt
        index = int(fields[2])
        system1 = fields[7]
        system2 = fields[9]
        system3 = fields[11]
        system4 = fields[13]
        system5 = fields[15]
        sentence1 = extract_sentence(path, system1, dir, index)
        sentence2 = extract_sentence(path, system2, dir, index)
        sentence3 = extract_sentence(path, system3, dir, index)
        sentence4 = extract_sentence(path, system4, dir, index)
        sentence5 = extract_sentence(path, system5, dir, index)
        entries = []
        entries.append((fields[16], system1, sentence1))
        entries.append((fields[17], system2, sentence2))
        entries.append((fields[18], system3, sentence3))
        entries.append((fields[19], system4, sentence4))
        entries.append((fields[20], system5, sentence5))
        entries.sort()
        source = extract_sourceref(path, src, index)

        write_rankings(source, entries, out_gt, out_lt, out_eq)

    out_gt.close()
    out_lt.close()
    out_eq.close()
    return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'USAGE: %s JUDGMENTS.CSV PATH' % sys.argv[0]
        print '\tpath = path to folder with evaluation raw data'
    else:
        input = codecs.open(sys.argv[1], 'r', 'utf-8')
        path = sys.argv[2]
        create_evaluation(input, path)
