import os
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from benchmarktool.runscript.benchmark.specs.base import BaseInstanceSpecification

class FolderSpec(BaseInstanceSpecification):
    def __init__(self, path, patterns=[], *args, **kwargs):
        super(__class__, self).__init__(path)
        self.patterns = (
            [ "**/*", "!**/.git", "!**/.svn", "!**/._*", "!**/0arch*"]
            + patterns
        )

    def setup(self, benchmark):
        patterns = map(GitWildMatchPattern, self.patterns)
        pathspec = PathSpec(patterns)

        for file in pathspec.match_tree(self.path):
            splitted_path = os.path.split(file)
            if len(splitted_path) == 1:
                relroot = "."
            else:
                relroot = os.path.join(*splitted_path[:-1])
            benchmark.addInstance(self.path, relroot, splitted_path[-1])
