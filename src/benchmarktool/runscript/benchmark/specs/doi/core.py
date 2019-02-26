class BaseDOIHandler:
    @classmethod
    def is_compatible(cls, doi):
        return False
    
    def __init__(self, doi, path):
        self.doi = doi
        self.path = path
    
    def setup(self):
        raise NotImplementedError
    
    def teardown(self):
        raise NotImplementedError

