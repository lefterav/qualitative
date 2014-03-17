from io_utils.sax.saxps2jcml import IncrementalJcml
from io_utils.sax.cejcml import CEJcmlReader

def join_jcml(filenames, output_filename):
    writer = IncrementalJcml(output_filename)
    for filename in filenames:
        reader = CEJcmlReader(filename, all_general=True, all_target=True)
        for parallelsentence in reader.get_parallelsentences():
            writer.add_parallelsentence(parallelsentence)
        print "_"     
    writer.close()

