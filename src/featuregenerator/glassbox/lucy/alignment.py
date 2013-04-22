# -*- coding: utf-8 -*-
import codecs
import re

from collections import defaultdict

from shared import load_moses_f2e, load_text, load_trees


def align_phrases(source, lucy, moses, path):
    """ This method loads the aligned trees and the source sentences and tries
    to find the best possible alignment between phrases inside the Lucy trees,
    the source text and the Moses translation.
    
    This will create a new file phrases.aligned containing all such alignments
    for each of the source sentences.  The exact format of this file is TBA.
    """
    sentences = load_text(source)
    translations = load_text('%s.output' % moses)
    f2e = load_moses_f2e('%s.f2e' % moses)
    trees = load_trees('%s/lucy-%s.aligned' % (path, '%s'))
        
    text2tree = []
    for s_id in xrange(len(sentences)):
        line = sentences[s_id]
        atree = trees['analysis'][s_id]
        t2t, non_aligned = align_text_to_tree(line, atree, [])
        text2tree.append(t2t)
    print '\t- successfully computed text-to-tree alignment.'
    
    alignment = []    
    for s_id in xrange(len(sentences)):
        # Load the trees that will be used to compute the alignment.
        analysis_tree = trees['analysis'][s_id]
        transfer_tree = trees['transfer'][s_id]
        generation_tree = trees['generation'][s_id]
        
        # Load the NPs from the previously loaded Lucy trees.
        nps = {
          'analysis': analysis_tree.elements('NP'),
          'transfer': transfer_tree.elements('NP'),
          'generation': generation_tree.elements('NP')
        }
        
        # We prevent double alignment by memorizing the ids of aligned NPs.
        ids = {
          'analysis': [],
          'transfer': [],
          'generation': []
        }
        
        # We will store the alignment for the current sentence in this list.
        phrases = []
    
        # Our NP alignment approach tries to connect an NP from the analysis
        # tree with an NP from the generation tree via an intermediate NP
        # inside the transfer tree.  If no such connection can be found, the
        # "empty" alignment to id -1 will be stored into the final alignment. 
        for a in nps['analysis']:
            _a = a.attrib
            
            # If the current NP does not have a lemma attribute, we cannot
            # align it and create an "empty" entry inside the alignment list.
            if not _a.has_key('lemma'):
                phrases.append((nps['analysis'].index(a), -1, -1))
                ids['analysis'].append(nps['analysis'].index(a))
                continue
            
            _range = eval(_a['range'])
            source_range = abs(int(_range[1]) - int(_range[0])) +1
            
            # The lemma is our first key, we look it up in the transfer tree.
            key = _a['lemma']
            
            for t in nps['transfer']:
                _t = t.attrib
                
                # We skip if the transfer NP has already been used.
                if nps['transfer'].index(t) in ids['transfer']:
                    continue
                
                # Check if the transfer range is plausible.
                _range = eval(_t['range'])
                transfer_range = abs(int(_range[1]) - int(_range[0])) +1
                if abs(source_range-transfer_range) >= 2:
                    continue
                
                # We try to find our key inside the transfer tree.
                if _t.has_key('source') and _t['source'] == key:
                    # Compute the second key, the target from the transfer NP.
                    if _t.has_key('target'):
                        key2 = _t['target']
                    
                    # If no target can be detected, we use the source instead.
                    else:
                        key2 = _t['source']
                    
                    # Finally, we try to find a matching generation tree NP.
                    for g in nps['generation']:
                        _g = g.attrib
                        
                        # Again, we skip if the generation NP was used before.
                        if nps['generation'].index(g) in ids['generation']:
                            continue
                        
                        # Check if the target range is plausible.
                        _range = eval(_g['range'])
                        target_range = abs(int(_range[1]) - int(_range[0])) +1
                        if abs(source_range-target_range) >= 2:
                            continue
                        
                        # If the generation NP matches, we have found a full
                        # alignment for analysis, transfer and generation.
                        if _g.has_key('lemma') and _g['lemma'] == key2 and \
                          nps['analysis'].index(a) not in ids['analysis']:
                            id_a = nps['analysis'].index(a)
                            id_t = nps['transfer'].index(t)
                            id_g = nps['generation'].index(g)
                        
                            phrases.append((id_a, id_t, id_g))
                        
                            ids['analysis'].append(id_a)
                            ids['transfer'].append(id_t)
                            ids['generation'].append(id_g)
        
        # Create "empty" entries for any remaining, non-aligned phrase.
        for a in nps['analysis']:
            if nps['analysis'].index(a) not in ids['analysis']:
                phrases.append((nps['analysis'].index(a), -1, -1))
        
        # We now have computed the phrase alignment for the current sentence.
        alignment.append(phrases)
    
    print '\t- successfully computed Lucy phrase alignment.'
        
    _log = codecs.open('%s/phrases.log' % path, 'w', 'utf-8')
    _nps = codecs.open('%s/phrases.aligned' % path, 'w', 'utf-8')
    _nps_source = codecs.open('%s/phrases.source' % path, 'w', 'utf-8')
        
    for s_id in xrange(len(sentences)):
        _log.write('sentence: %r\n\n' % sentences[s_id])
        
        atree = trees['analysis'][s_id]
        ttree = trees['transfer'][s_id]
        gtree = trees['generation'][s_id]
        
        anps = atree.elements('NP')
        tnps = ttree.elements('NP')
        gnps = gtree.elements('NP')
        
        phrases = alignment[s_id]
        t2t = text2tree[s_id]
        
        _data = []
        for phrase in phrases:
            _data.append('%d=%d=%d' % phrase)
            
            _r = eval(anps[phrase[0]].attrib['range'])
            source_range = range(_r[0], _r[1]+1)
            
            source_ids = []
            for w_id, t_ids in t2t:
                for t_id in t_ids:
                    if t_id in source_range and not w_id in source_ids:
                        source_ids.append(w_id)
            
            target_ids = []
            for w_id in source_ids:
                if f2e[s_id].has_key(w_id):
                    target_ids.extend(f2e[s_id][w_id])
            
            target_ids = filter(lambda x: x > -1, target_ids)
            _tmp_ids = []
            [_tmp_ids.append(x) for x in target_ids if not _tmp_ids.count(x)]            
            target_ids = _tmp_ids
            
            if len(source_ids) and len(target_ids):
                _source = ','.join([str(x) for x in source_ids])
                _target = ','.join([str(x) for x in target_ids])
                _data[-1] += '|%s=%s' % (_source, _target)
            
                _source = [sentences[s_id].split()[x] for x in source_ids]
                _target = [translations[s_id].split()[x] for x in target_ids]
            
                _log.write('Moses:\n%r\n->\n%r\n\n' % \
                  (u' '.join(_source), u' '.join(_target)))
                _nps_source.write('%s\n' % u' '.join(_source))
            
            if phrase[2] > 0:
                _log.write('Lucy:\n%r\n->\n%r\n---\n\n' % \
                  (atree.text(anps[phrase[0]]), gtree.text(gnps[phrase[2]])))
            else:
                _log.write('Lucy:\n%r\n->\n??\n---\n\n' % \
                  atree.text(anps[phrase[0]]))
        
        _nps.write('%s\n' % ' '.join(_data))
    
    _nps_source.close()
    _nps.close()
    _log.close()
    print '\t- wrote "%s/phrases.log".' % path
    print '\t- wrote "%s/phrases.aligned".' % path
    print '\t- wrote "%s/phrases.source".' % path


def align_trees(source, lucy, path):
    """ This method computes the sentence to tree alignment between the given
    source sentences and the Lucy trees stored inside the folder specified by
    the given path.
    
    Once the alignment has been computed, 3 new files will be created:
    lucy-analysis.aligned, lucy-transfer.aligned, and lucy-generation.aligned.
    These files should contain exactly as many lines as there are sentences in
    the source file.  Multiple trees inside one line are separated by \t tabs.
    """
    sentences = load_text(source)    
    trees = load_trees('%s/lucy-%s' % (path, '%s'), ['analysis'])
    
    sentence_to_trees = align_sentences_to_trees(path, sentences,
      trees['analysis'])
    print '\t- successfully computed sentence-to-tree alignment.'
    
    del(sentences)
    del(trees)

    for key in ['analysis', 'transfer', 'generation']:
        trees = load_text('%s/lucy-%s' % (path, key))
        
        _filename = '%s/lucy-%s.aligned' % (path, key)
        _out = codecs.open(_filename, 'w', 'utf-8')
        for s_id, t_ids in sentence_to_trees:
            _data = '\t'.join([trees[x] for x in t_ids])
            _out.write('%s\n' % _data)
        _out.close()
        del(trees)
        
        print '\t- wrote "%s/lucy-%s.aligned".' % (path, key)


def score_tree_for_sentence(tree, sentence, removeMatches=True):
    """ Computes the number of surface forms that are contained in both the
    given tree text and the sentence. Measures ``compatibility'' between both.
    sentence is a list of surface words, matched words will be removed from
    the list if keyword parameter removeMatches is set to True. Comparison is
    done on lowercased Strings to avoid problems.
    """
    surface_forms = [x.strip() for x in tree.text(tree.get_root()).split()]
    
    for key in ['$', '<EMPTY>']:
        while key in surface_forms:
            surface_forms.remove(key)

    surface_forms = map(unicode.lower, surface_forms)

    result = 0
    for surface in surface_forms:
        if surface in sentence:
            result += 1
            if removeMatches:
                sentence.remove(surface)
        
        # We allow "prefix" matches if the surface is at least 2 characters!
        elif len(surface) > 1:
            prefixes = filter(lambda x: x.startswith(surface), sentence)
            if len(prefixes):
                result += 1
                if removeMatches:
                    sentence.remove(prefixes[0])
    
    return result


def align_sentences_to_trees(path, sentences, trees):
    """ Takes a list of sentences and tree objects and computes the best
    alignment between them, possibly mapping a sentence to multiple trees.

    Returns the alignment as a list of tuples, alignment to the empty list
    means that the respective sentence could not be aligned to any tree.
    """
    alignment = defaultdict(list)
    t_id = 0
    s_id = 0
    steps = 0
    
    cache = [x.strip().lower() for x in sentences[s_id].split()]
    cache_next = []
    
    while t_id < len(trees) and s_id+1 < len(sentences):
        steps += 1
        
#        print "steps: {0}, t_id: {1}, s_id: {2}\n".format(steps, t_id, s_id)
#        print cache, "\n"
                
        # Compute score for current tree and sentence cache.
        score_k = score_tree_for_sentence(trees[t_id], cache)
#        print "score_k: {0}".format(score_k)
#        print "cleaned cache: {0}\n".format(cache)
        
        if score_k / float(len(sentences[s_id].split())) > .9:
#            print "> .9 ruleia"
            alignment[s_id].append(t_id)
            t_id += 1
            continue
        
        # We compare this score to the "possible" score for the next sentence.
        cache_next = [x.strip().lower() for x in sentences[s_id+1].split()]
        score_k_next = score_tree_for_sentence(trees[t_id], cache_next, False)
        
#        print "cache_next: {0}".format(cache_next)
#        print "score_k_next: {0}".format(score_k_next)
        
        if score_k == 0 and score_k_next == 0:
            print "WARNING - zero scores for s_id:{0}, t_id:{1}".format(
              s_id, t_id)
            alignment[s_id+1].append(t_id)
            s_id += 1
            t_id += 1
            cache = cache_next
            continue
        
        if score_k >= score_k_next:
#            print "score_k >= score_k_next: t_id++"
            alignment[s_id].append(t_id)
            t_id += 1
        
        else:
#            print "score_k < score_k_next: s_id++"
            s_id += 1
            cache = cache_next
    
    if t_id < len(trees):
        alignment[s_id].append(t_id)

    for i in range(len(sentences)):
        if i not in alignment.keys():
            print "WARNING - missing key: {0}".format(i)
            if i+1 in alignment.keys() and len(alignment[i+1]) > 1:
                print "WARNING - applying self-healing patch!"
                alignment[i] = [alignment[i+1][0]]
                alignment[i+1] = alignment[i+1][1:]

    result = [(key, value) for key, value in alignment.items()]
    
    # Write out alignment.log
    _log = codecs.open('%s/alignment.log' % path, 'w', 'utf-8')
    for s_id, t_ids in result:
        tree_texts = []
        for t_id in t_ids:
            tree = trees[t_id]
            tree_texts.append(tree.text(tree.__tree__.getroot()).strip('$'))

        tree_text = u' '.join([x.strip() for x in tree_texts])
        tree_text = tree_text.replace('<EMPTY>', '')
        
        _log.write(' s_id: {0}\n'.format(s_id))
        _log.write(' text: %r\n' % sentences[s_id])
        _log.write('trees: %r\n' % tree_text)
        _log.write('---\n\n')
    
    _log.close()
    print '\t- wrote "%s/alignment.log".' % path
    assert(len(alignment.keys()) == len(sentences))

    return result


def align_text_to_tree(text, tree, words):
    """ Aligns the given text sequence with the given tree object.
    
    The words list parameter allows to pass in the list of words that we want
    to find alignments for.  This is usually needed if a source sentence is
    aligned to several tree objects.  Please note that source word ids should
    be "stable" when used with several trees.  As long as the words array is
    taken from the previous align_text_to_tree call's non-aligned list, the
    ids are guaranteed to be correct wrt. the source sentence.
    
    The function returns a tuple containing the alignment in the first
    position and the non-aligned source words as a list in the second place.
    """
    # First, we collect all terminals from the given tree and convert surfaces
    # containing multiple words into several entries containing only one word.
    # This is needed in order to allow the alignment algorithm to function.
    terminals = tree.terminals(tree.__tree__.getroot())
    terminals = list(enumerate(terminals))
    terminals = filter(lambda x: x[1][0] != '$', terminals)
    
    # Replace multi-word surface terminals by single-word surface terminals.
    _terminals = []
    for t in terminals:
        surface = ['']
        if t[1][1].has_key('surface'):
            surface = t[1][1]['surface'].split()
        
        for s in surface:
            terminal = t[1]
            values = terminal[1].copy()
            values['surface'] = '%s' % unicode(s)
            _terminals.append((t[0], (terminal[0], values)))
        
    terminals = _terminals
    terminal_ids = []
    [terminal_ids.append(x[0]) for x in terminals]
    
    # If words is not given, we build it from the given text.
    if not len(words):
        words = list(enumerate(unicode(text).split()))
    
    # Once the words alignment is computed, we can start aligning the text to
    # the given tree object.
    alignment = []
    cache = []
    haystack = None
    used_word_ids = []
    used_terminal_ids = []
    
    for w_id, word in words:
        # Skip if the current word has already been aligned.
        if w_id in used_word_ids:
            continue
        
        for t_id, terminal in terminals:
            # Also skip for used up terminals.
            if used_terminal_ids.count(t_id) == terminal_ids.count(t_id):
                continue
            
            # If our cache is empty, the current word becomes the haystack.
            if not len(cache):
                haystack = unicode(word)
                
                # We perform some Lucy special symbol conversions.
                haystack = haystack.replace(u'ä', 'ae')
                haystack = haystack.replace(u'ö', 'oe')
                haystack = haystack.replace(u'ü', 'ue')
                haystack = haystack.replace(u'ß', 'ss')
            
            data = terminal[1]
            if data.has_key('surface'):
                surface = data['surface'].strip()
                
                # If the current terminal surface matches the haystack, we
                # have found an alignment of the terminals inside the cache
                # with the current word.  We add this alignment to the list
                # of alignments and continue with the next word.
                if haystack == surface:
                    # The current terminal also belongs to the alignment!
                    cache.append(t_id)
                    
                    # Update the lists of used words/terminals.
                    used_word_ids.append(w_id)
                    used_terminal_ids.extend(cache)
                    
                    # Update the alignment list.
                    alignment.append((w_id, cache))
                    
                    # Clear the cache and break the loop over all terminals.
                    cache = []
                    break
                
                # Otherwise, if the haystack only starts with the current tree
                # surface, we add the current terminal id to the cache and try
                # to look up the haystack using the next terminal(s).
                elif haystack.startswith(surface):
                    # The current terminal belongs to the alignment!
                    cache.append(t_id)
                    
                    # Update the haystack by removing the part that matches
                    # the current terminal surface.
                    haystack = haystack[len(surface):].strip()
                    continue
            
            # If the current surface does not match, we reset the cache.
            if len(cache):
                cache = []
    
    words = filter(lambda x: x[0] not in used_word_ids, words)
    
    return (alignment, words)
