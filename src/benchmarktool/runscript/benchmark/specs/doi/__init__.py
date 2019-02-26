from ..folder import FolderSpec
from .zenodo import ZenodoHandler


class DOISpec(FolderSpec):
    handlers = [
        ZenodoHandler
    ]
    
    def __init__(self, path, doi, extract_archives=True, *args, **kwargs):
        super(__class__, self).__init__(path, *args, **kwargs)
        self.doi = doi
        self.extract_archives = extract_archives
        self.handler = None
        for Handler in self.handlers:
            if Handler.is_compatible(self.doi):
                self.handler = Handler(self.doi, path)
                break
        
        if self.handler is None:
            raise RuntimeError("doi not supported")


    def setup(self, benchmark):
        self.handler.setup(extract_archives=self.extract_archives)
        super(__class__, self).setup(benchmark)
