"""Extracts the BAD file and target text from the given message file."""
# -*- coding: utf-8 -*-
__author__ = "Christian Federmann <cfedermann@dfki.de>"

import sys
from TranslationRequestMessage_pb2 import TranslationRequestMessage


def usage(scriptname):
    """Returns usage information as multi-line String."""
    usage_info = """
\tusage: {0} <message-file> <splitter-token>
""".format(scriptname)
    
    return usage_info


def _write_out_trees(message, filename):
    """Opens the given message file and writes out trees to .BAD file."""
    packet_data = [(x.key, x.value) for x in message.packet_data]
    
    outfile = open('{0}.BAD'.format(filename), 'w')
    for key, value in packet_data:
        if key == 'TREES':
            outfile.write(unicode(value).encode('utf-8'))
    outfile.close()


def _write_out_result(message, filename, splitter_token):
    """Opens the given message file and writes out target text to file."""
    outfile = open('{0}.target'.format(filename), 'w')
    result = unicode(message.target_text).encode('utf-8')
    result = result.replace('{0}\n'.format(splitter_token), '')
    outfile.write(result)
    outfile.close()


def main(source_file, splitter_token):
    """Extracts the BAD file and target text from the given message file."""
    handle = open(source_file, 'r+b')
    message = TranslationRequestMessage()
    message.ParseFromString(handle.read())
    handle.close()

    _write_out_trees(message, source_file)
    _write_out_result(message, source_file, splitter_token)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print usage(sys.argv[0])
        sys.exit(-1)

    # Bind command line arguments.
    SOURCE_FILE = sys.argv[1]
    SPLITTER_TOKEN = sys.argv[2]

    # Call main routine.
    main(SOURCE_FILE, SPLITTER_TOKEN)

    sys.exit(0)