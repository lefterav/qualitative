from io.input.xliffreader import XliffReader
from io.output.taraxuwriter import TaraXUWriter

dataset = XliffReader("/home/lefterav/workspace/TaraXUscripts/metawp2/lucy.xlf")
TaraXUWriter(dataset).write_to_file("/home/lefterav/taraxu_data/ml4hmt/test.xml")
