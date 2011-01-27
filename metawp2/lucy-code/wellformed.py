"""Uses the Expat library to determine if an XML document is well-formed."""
# -*- coding: utf-8 -*-
__author__ = "Christian Federmann <cfedermann@dfki.de>"

import sys
import xml.parsers.expat
from glob import iglob

def usage(scriptname):
    """Returns usage information as multi-line String."""
    usage_info = """
\tusage: {0} <xml-file(s)> [xml-file(s)...]
""".format(scriptname)
    
    return usage_info


def _parsefile(xml_file):
    """Tries to parse the given XML file using Expat."""
    parser = xml.parsers.expat.ParserCreate()
    parser.ParseFile(open(xml_file, 'r'))
    parser = None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print usage(sys.argv[0])
        sys.exit(-1)
    
    # Iterate over all given command line arguments.
    for arg in sys.argv[1:]:
        # Use iglob to determine all filenames from current argument.
        for filename in iglob(arg):
            try:
                _parsefile(filename)
                print "[VALID] {0} is well-formed.".format(filename)
            
            except Exception, e:
                print "[ERROR] {0} has problems: \"{1}\".".format(filename, e)
