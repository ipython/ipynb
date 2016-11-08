"""
FileSystem based importer for ipynb / .py files.

If you prefix module names with 'ipynb.fs', it'll try to treat them exactly
the same way as .py files. All the output is ignored, and all the code is imported
as if the cells were linearly written to be in a flat file.
"""
import sys
from importlib.machinery import SourceFileLoader

from ipynb.utils import get_code
from ipynb.fs.finder import FSFinder


class NotebookLoader(SourceFileLoader):
    def get_code(self, fullname):
        if self.path.endswith('.ipynb'):
            with open(self.path) as f:
                return self.source_to_code(get_code(f.read()), self.path)
        else:
            return super().get_code(fullname)


sys.meta_path.append(FSFinder(__package__, NotebookLoader))
