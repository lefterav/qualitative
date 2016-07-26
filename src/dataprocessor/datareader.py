class DataReader:
    """
    Abstract base class for classes reading data. To be moved to a more suitable module, when possible. 
    """

    
    def get_attribute_sets(self):
        raise NotImplementedError()
    
    def get_dataset(self):
        raise NotImplementedError()
    
    def get_parallelsentences(self, **kwargs):
        raise NotImplementedError()
    
    def __iter__(self):
        return self.get_parallelsentences()