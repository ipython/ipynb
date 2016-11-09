"""
FileSystem based importer for ipynb / .py files.

If you prefix module names with 'ipynb.fs', it'll try to treat them exactly
the same way as .py files. All the output is ignored, and all the code is imported
as if the cells were linearly written to be in a flat file.
"""
import sys
import json
from importlib.machinery import SourceFileLoader

from ipynb.utils import get_code, validate_nb
from ipynb.fs.finder import FSFinder


class NotebookLoader(SourceFileLoader):
    def get_code(self, fullname):
        if self.path.endswith('.ipynb'):
            with open(self.path) as f:
                nb = json.load(f)
                if not validate_nb(nb):
                    raise ImportError('Could not import {path} for {fn}: not a valid ipynb file'.format(
                        path=self.path,
                        fn=fullname
                    ))
                return self.source_to_code(get_code(nb), self.path)
        else:
            return super().get_code(fullname)


sys.meta_path.append(FSFinder(__package__, NotebookLoader))
