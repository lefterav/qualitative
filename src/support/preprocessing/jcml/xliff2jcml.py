from dataprocessor.input.xliffreader import XliffReader
from dataprocessor.output.xmlwriter import XmlWriter
from dataprocessor.sax.saxwrapper import SaxWrapper
from sys import argv
from xml import sax



input_xml_filename = argv[1]
output_filename = argv[2]
#dataset = XliffReader(input_xml_filename).get_dataset()
#XmlWriter(dataset).write_to_file(output_filename)
saxwrapper = SaxWrapper("trans-unit", reader = XliffReader, writer = XmlWriter, filename_out = output_filename)
source = open(input_xml_filename)
sax.parse(source, saxwrapper)
source.close()



