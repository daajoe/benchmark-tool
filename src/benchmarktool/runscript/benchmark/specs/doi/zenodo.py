import os
import requests
from zipfile import ZipFile
from dotmap import DotMap
from benchmarktool.runscript.benchmark.specs.doi.core import BaseDOIHandler
from benchmarktool.tools import mkdir_p, download_file


class ZenodoHandler(BaseDOIHandler):
    # Sandbox
    api_url = "https://sandbox.zenodo.org/api"
    doi_prefix = "10.5072/zenodo."

    # # Production
    # api_url = "https://zenodo.org/api"
    # doi_prefix = "10.5281/zenodo."

    @classmethod
    def is_compatible(cls, doi):
        # example: 10.5281/zenodo.1289383
        return doi.startswith(cls.doi_prefix)

    def get_record(self):
        if not hasattr(self, "record") or self.record is None:
            record_id = self.doi[len(self.doi_prefix):] # remove doi_prefix
            url = "{}/records/{}".format(self.api_url, record_id)
            self.record = DotMap(requests.get(url).json())

        return self.record
    
    def extract_zip(self, path):
        extract_path = path[:-len(".zip")]
        if not os.path.isdir(extract_path):
            with ZipFile(path) as zip:
                zip.extractall(extract_path)

    def setup(self, skip_existing=True, extract_archives=True):
        record = self.get_record()

        mkdir_p(self.path)
        for file in record.files:
            path = os.path.join(self.path, file.key)
            if skip_existing and not os.path.isfile(path):
                download_file(file.links.self, path)
            if file.type == "zip":
                self.extract_zip(path) 

    def teardown(self):
        # @TODO should we rmdir -r $(self.path)?
        pass
