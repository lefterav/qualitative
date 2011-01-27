"""Inserts splitter_tokens to separate sentences from source_file."""
# -*- coding: utf-8 -*-
__author__ = "Christian Federmann <cfedermann@dfki.de>"

import sys


def usage(scriptname):
    """Returns usage information as multi-line String."""
    usage_info = """
\tusage: {0} <source-file> <splitter-token> [output-file]
""".format(scriptname)
    
    return usage_info


def main(source_file, splitter_token, output_file):
    """Inserts splitter_tokens to separate sentences from source_file."""
    with open(source_file, 'r') as source:
        for line in source:
            output_file.write("""{0}\n{1}\n""".format(line.strip(),
              splitter_token))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print usage(sys.argv[0])
        sys.exit(-1)
    
    # Bind command line arguments.
    SOURCE_FILE = sys.argv[1]
    SPLITTER_TOKEN = sys.argv[2]
    
    # If given, open output file object, otherwise write to stdout.
    if len(sys.argv) > 3:
        OUTPUT_FILE = open(sys.argv[3], 'w')
    else:
        OUTPUT_FILE = sys.stdout
    
    # Call main routine.
    main(SOURCE_FILE, SPLITTER_TOKEN, OUTPUT_FILE)
    
    # If opened, close given output file object.
    if len(sys.argv) > 3:
        OUTPUT_FILE.close()
    
    sys.exit(0)