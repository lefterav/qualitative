"""Extracts and segments Lucy trees from the given BAD file."""
# -*- coding: utf-8 -*-
__author__ = "Christian Federmann <cfedermann@dfki.de>"

import sys
from os import unlink
from LucyTrees import AnalysisTree, TransferTree, GenerationTree


WAIT_MODE = 0
ANALYSIS_MODE = 1
TRANSFER_MODE = 2
GENERATION_MODE = 3


def usage(scriptname):
    """Returns usage information as multi-line String."""
    usage_info = """
\tusage: {0} <BAD-file> <splitter-token> [output-file-prefix]
""".format(scriptname)
    
    return usage_info


def _extract_trees(bad_file, splitter_token, prefix, block_size=1024*1024):
    """Extracts Lucy trees from the given BAD file."""
    sections = ('analysis', 'transfer', 'generation')
    sections_close_tags = tuple(['</{0}>'.format(x) for x in sections])
    
    _mode = WAIT_MODE
    _text = None

    # Extract Lucy data from all interesting sections and collect text.
    with open(bad_file, 'r') as source:
        for line in source:
            stripped = line.strip()
            
            # Check whether we have left a section.
            if stripped in sections_close_tags:
                _mode = WAIT_MODE
                if _text:
                    _text.close()
                    _text = None
            
            # If we are inside a section, add content to _text dictionary.
            if _mode != WAIT_MODE:
                _text.write(' {0}'.format(stripped))
                _text.flush()
            
            # Otherwise, change the mode parameter wrt. the current input.
            if stripped == '<analysis>':
                _mode = ANALYSIS_MODE
                assert(_text == None)
                _text = open('{0}-analysis.tmp'.format(prefix), 'w')
            
            elif stripped == '<transfer>':
                _mode = TRANSFER_MODE
                assert(_text == None)
                _text = open('{0}-transfer.tmp'.format(prefix), 'w')
            
            elif stripped == '<generation>':
                _mode = GENERATION_MODE
                assert(_text == None)
                _text = open('{0}-generation.tmp'.format(prefix), 'w')
        
        # Close any open file handle.
        if _text:
            _text.close()

        print '\t- successfully loaded data from "{0}".'.format(bad_file)

        # Now we have all text for each of the three sections.  As several
        # lines belong to one sentence, we now have to fix the sentences.
        sentences = dict([(x, 0) for x in sections])
        trees = []
        for key in sections:
            _sentences = open('{0}-{1}'.format(prefix, key), 'w')
            _text = open('{0}-{1}.tmp'.format(prefix, key), 'r')
            _opened_parentheses = 0
            _in_string = False
            _last = 0
            _splitter = '$ {0} $'.format(splitter_token)
            
            if key == 'analysis':
                tree_init = AnalysisTree
            elif key == 'transfer':
                tree_init = TransferTree
            elif key == 'generation':
                tree_init = GenerationTree

            new = _text.read(block_size)
            value = ' {0}'.format(new)
            while new.strip() != '':
                _index = 0
                while _index < len(value):
                    # Check whether we are entering/exiting String mode.
                    if value[_index] == '"' and value[_index-1] != '\\':
                        _in_string = not _in_string
                        _index += 1
                        continue

                    # If we are not in String mode, check parentheses.
                    if not _in_string:
                        if value[_index] == '(':
                            _opened_parentheses += 1

                        elif value[_index] == ')':
                            _opened_parentheses -= 1

                            if _opened_parentheses == 0:
                                _sentence = value[_last:_index+1].strip()
                                
                                # Create tree object from _sentence.
                                _tree = tree_init(_sentence)
                                _tree_text = _tree.text(_tree.get_root())
                                _tree = None

                                if _tree_text == _splitter:
                                    _trees = '\t'.join(trees)
                                    _sentences.write('{0}\n'.format(_trees))
                                    _sentences.flush()
                                    trees = []
                                    sentences[key] += 1
                                
                                else:
                                    trees.append(_sentence)
                                
                                _last = _index + 1

                    _index += 1
                
                new = _text.read(block_size)
                value = ' {0}{1}'.format(value[_last:], new)

                _last = 0
                _opened_parentheses = 0
                _in_string = False

            # Close output file.
            _sentences.close()
            print '\t- wrote "{0}-{1}".'.format(prefix, key)
            
            # Delete temporary file.
            unlink('{0}-{1}.tmp'.format(prefix, key))

        # All three files must contain the same number of trees, otherwise it
        # will not be possible to compute alignments in subsequent steps!
        assert sentences['analysis'] == sentences['transfer'] \
          == sentences['generation']
        print '\t- extracted {0} trees from "{1}" file.'.format(
          sentences['analysis'], bad_file)


def main(bad_file, splitter_token, output_file_prefix):
    """Extracts and segments Lucy trees from the given BAD file."""
    _extract_trees(bad_file, splitter_token, output_file_prefix)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print usage(sys.argv[0])
        sys.exit(-1)
    
    # Bind command line arguments.
    BAD_FILE = sys.argv[1]
    SPLITTER_TOKEN = sys.argv[2]
    
    # If given, bind output file prefix from command line.
    if len(sys.argv) > 3:
        OUTPUT_FILE_PREFIX = sys.argv[3]
    else:
        OUTPUT_FILE_PREFIX = "lucy"
    
    # Call main routine.
    main(BAD_FILE, SPLITTER_TOKEN, OUTPUT_FILE_PREFIX)
    
    sys.exit(0)
