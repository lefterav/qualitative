from io.input.xliffreader import XliffReader
from io.output.xmlwriter import XmlWriter
from io.sax.saxwrapper import SaxWrapper
from sys import argv
from xml import sax

input_filename = argv[1]
output_filename = argv[2]
#dataset = XliffReader(input_filename).get_dataset()
#XmlWriter(dataset).write_to_file(output_filename)
saxwrapper = SaxWrapper("trans-unit", reader = XliffReader, writer = XmlWriter, filename_out = output_filename)
source = open(input_filename)
sax.parse(source, saxwrapper)
source.close()

