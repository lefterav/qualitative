'''
Created on Aug 4, 2011

@author: elav01
'''


from sentence.dataset import DataSet


class GenericReader(object):
    '''
    classdocs
    '''
    
    def __init__(self, input_filename, load = True):
        """
        Constructor. Creates an XML object that handles ranking file data
        @param input_filename: the name of XML file
        @type input_filename: string
        @param load: by turning this option to false, the instance will be 
                     initialized without loading everything into memory
        @type load: boolean 
        """
        self.input_filename = input_filename
        self.loaded = load
        if load:
            self.load()
    

    
    def load(self):
        raise NotImplementedError( "Should have implemented this" )

        
    
    def unload(self):
        raise NotImplementedError( "Should have implemented this" )

            

    def get_dataset(self):
        """
        Returns the contents of the parsed file into an object structure, which is represented by the DataSet object
        Note that this will cause all the data of the file to be loaded into system memory at once. 
        For big data sets this may not be optimal, so consider sentence-by-sentence reading with SAX (e.g. saxjcml.py)
        @return the formed data set
        @rtype DataSet
        """
        return DataSet(self.get_parallelsentences())
        
    def get_parallelsentences(self):
        raise NotImplementedError( "Should have implemented this" )

    
    
   

        