"""Creates XLIFF annotation files for the given sentences/Lucy trees."""
# -*- coding: utf-8 -*-
__author__ = "Christian Federmann <cfedermann@dfki.de>"


import sys
from os import mkdir

def usage(scriptname):
    """Returns usage information as multi-line String."""
    usage_info = """
\tusage: {0} <source-text> <target-text> <source-lang> <target-lang> \
<tree-file-prefix>
""".format(scriptname)
    
    return usage_info


def _create_alt_trans(src_text, tgt_text, src_lang, tgt_lang):
    """Creates the <alt-trans...> tag."""
    xml_template = """
    <alt-trans rank="1" tool-id="t2">
        <source xml:lang="{0}">{1}</source>
        <target xml:lang="{2}">{3}</target>"""
    return xml_template.format(src_lang, src_text, tgt_lang, tgt_text)


def _close_alt_trans():
    """Closes the <alt-trans...> tag."""
    xml_template = """
    </alt-trans>"""
    return xml_template


def _create_derivation(derivation_type, derivation_id, sentence_id):
    """Creates the <add:derivation...> tag."""
    xml_template = """
        <add:derivation type="lucy{0}" id="s{1}_t2_r1_d{2}">"""
    return xml_template.format(derivation_type, sentence_id, derivation_id)


def _close_derivation():
    """Closes the <add:derivation...> tag."""
    xml_template = """
        </add:derivation>
"""
    return xml_template


def _create_annotations(node):
    """Creates all <annotation...> tags for the given node."""
    _annotations = []
    for key, value in node.attributes.items():
        _tag = '\t\t\t\t<annotation type="{0}" value="{1}" />'.format(
          key.lower(), value)
        _annotations.append(_tag)
    
    # If there exists an "ALO" annotation, use it to fill <string...>.
    if 'ALO' in node.attributes.keys():
        _tag = '\t\t\t\t<string>{0}</string>'.format(node.attributes['ALO'])
        _annotations.append(_tag)
    
    return '\n'.join(_annotations)


def _create_token(node, derivation_id, sentence_id):
    """Creates a <token...> tag."""
    xml_template = """
            <token {0}id="{1}">{2}
            </token>"""
    # Generate children ids for this node.
    _children = ""
    if node.children:
        _addresses = []
        for child_node in node.children:
            _address = 's{0}_t2_r1_d{1}_k{2}'.format(sentence_id,
              derivation_id, child_node.node_id)
        
        _children = ','.join(_addresses)
    
    # Generate token id for this node.
    _token_id = 's{0}_t2_r1_d{1}_k{2}'.format(sentence_id, derivation_id,
      node.node_id)
      
    # Create annotation tags for this node.
    _annotations = '\n{0}'.format(_create_annotations(node))
    
    return xml_template.format(_children, _token_id, _annotations)


class TreeNode(object):
    """Basic tree class to create token information from Lucy trees."""
    _simple_attrs = ('CAT', 'SL-CAT', 'TL-CAT')
    _complex_attrs = ('CAN', 'ALO', 'SL-CAN', 'TL-CAN')

    def __init__(self, node_id=0, segment=''):
        """Creates and initializes a new tree node object."""
        self.attributes = {}
        self.children = []
        self.node_id = node_id
        self.parent = None
        
        if segment:
            for attribute in self._simple_attrs:
                _attr = '{0} '.format(attribute)
                if segment.count(_attr):
                    _value = segment.partition(_attr)[2].partition(' ')[0]
                    self.attributes[attribute] = _value
            
            for attribute in self._complex_attrs:
                _attr = '{0} "'.format(attribute)
                if segment.count(_attr):
                    _value = segment.partition(_attr)[2].partition('"')[0]
                    self.attributes[attribute] = _value


def _read_files(src_file, tgt_file):
    """Reads in source and target text files."""
    source_text = []
    with open(src_file, 'r') as source:
        for line in source:
            source_text.append(line.strip())

    target_text = []
    with open(tgt_file, 'r') as target:
        for line in target:
            target_text.append(line.strip())

    # Assert that all files contain the same number of sentences.
    assert(len(source_text) == len(target_text))

    # Return tuple containing the loaded sentences.
    return (source_text, target_text)


def _read_trees(tree_file_prefix, key):
    """Reads in Lucy trees for the given derivation type."""
    # Read in Lucy trees for the current derivation type.
    with open('{0}-{1}'.format(tree_file_prefix, key), 'r') as lucy_trees:
        trees = []
        for line in lucy_trees:
            trees.append(line.strip())
    
    return trees


def main(src_file, tgt_file, src_lang, tgt_lang, tree_file_prefix):
    """Creates XLIFF annotation files for the given sentences/Lucy trees."""
    try:
        # Create output folder if not existing yet.
        mkdir('{0}.output'.format(tree_file_prefix))
    
    except OSError:
        # Give warning as existing files might be overwritten.
        print 'Directory "{0}.output" already exists!'.format(
          tree_file_prefix)
    
    # We handle Lucy trees for the following derivation types.
    derivations = {'analysis': 1, 'transfer': 2, 'generation': 3}
        
    # Read in source and target sentences.
    source_text, target_text = _read_files(src_file, tgt_file)
    
    # For each derivation type, create ???
    for key in ('analysis', 'transfer', 'generation'):
        sys.stdout.write('{0:>10}: '.format(key.upper()))
        
        # Read in Lucy trees for the current derivation type.
        trees = _read_trees(tree_file_prefix, key)

        # Assert that the number of trees equals the number of sentences.
        assert(len(source_text) == len(trees))

        # Iterate over the loaded sentence trees and generate XLIFF.
        sentence_id = 0
        for tree in trees:
            # We use 1-based counters, so we increment here.
            sentence_id += 1
            
            # Create root node for this sentence.
            current_node = TreeNode()
            node_id = 1
            
            # Loop over the given tree source and create corresponding nodes.
            for i in xrange(len(tree)):
                # This indicates the begin of a tree segment.
                if tree[i:i+2] == '((':
                    _segment = tree[i:].partition(')')[0].strip('(')
                    
                    # Keep track of current node and create new node object.
                    parent_node = current_node
                    current_node = TreeNode(node_id, _segment)
                    
                    # Connect tree nodes.
                    parent_node.children.append(current_node)
                    current_node.parent = parent_node
                    
                    # Increase node id.
                    node_id += 1
                    
                # This indicates the end of a tree segment.
                if tree[i:i+2] == '))':
                    current_node = current_node.parent

            xml_buffer = ''
            # Create XML opening tag in "analysis" mode.
            if key == 'analysis':
                xml_buffer = _create_alt_trans(source_text[sentence_id-1],
                  target_text[sentence_id-1], src_lang, tgt_lang)

            # Create <add:derivation...> tag.
            xml_buffer += _create_derivation(key, derivations[key],
              sentence_id)

            # Create token tags for this derivation starting from first child.
            children_list = current_node.children
            while children_list:
                i = 1
                for child_node in children_list[0].children:
                    children_list.insert(i, child_node)
                    i += 1

                # Create XML annotation for current node.
                _token = _create_token(children_list[0], derivations[key],
                  sentence_id)
                xml_buffer += _token

                # Removes already processed node.
                children_list.pop(0)
            
            # Close <add:derivation...> tag.
            xml_buffer += _close_derivation()

            # Create XML closing tag in "generation" mode.
            if key == 'generation':
                xml_buffer += _close_alt_trans()
            
            # Convert & to &amp; and strip superfluous newlines.
            xml_buffer = xml_buffer.replace('&', '&amp;').strip('\n')
            xml_buffer = xml_buffer.replace('\n\n', '\n')
            
            # Show progress bar printing a dot every 4%.
            if sentence_id % (len(trees)/25) == 0:
                sys.stdout.write('.')
                sys.stdout.flush()

            # Only set output type to 'w' when storing analysis derivations.
            output_type = 'r+'
            if key == 'analysis':
                output_type = 'w'
            
            # Write out current XML buffer to output file.
            output_file = '{0}.output/t2-{1}-{2}-{3:04d}.xml'.format(
              tree_file_prefix, src_lang, tgt_lang, sentence_id)
            
            with open(output_file, output_type) as writer:
                writer.seek(0, 2)
                writer.write(xml_buffer)

        # Print a newline after the current derivation phase is finished.
        sys.stdout.write('\n')


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print usage(sys.argv[0])
        sys.exit(-1)

    # Bind command line arguments.
    SOURCE_FILE = sys.argv[1]
    TARGET_FILE = sys.argv[2]
    SOURCE_LANG = sys.argv[3].lower()
    TARGET_LANG = sys.argv[4].lower()
    TREE_FILE_PREFIX = sys.argv[5]

    # Call main routine.
    main(SOURCE_FILE, TARGET_FILE, SOURCE_LANG, TARGET_LANG, TREE_FILE_PREFIX)

    # Exit cleanly.
    sys.exit(0)
