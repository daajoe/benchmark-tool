class BaseInstanceSpecification:
    def __init__(self, path, *args, **kwargs):
        self.path = path

    def setup(self, benchmark):
        raise NotImplementedError
    
    def teardown(self):
        pass
