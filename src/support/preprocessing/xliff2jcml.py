from io.input.xliffreader import XliffReader
from io.output.xmlwriter import XmlWriter
from sys import argv

input_filename = argv[1]
output_filename = argv[2]
dataset = XliffReader(input_filename).get_dataset()
XmlWriter(dataset).write_to_file(output_filename)
