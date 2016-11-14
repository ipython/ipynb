"""
FileSystem based importer for ipynb / .py files.

If you prefix module names with 'ipynb.fs', it'll try to treat them exactly
the same way as .py files. All the output is ignored, and all the code is imported
as if the cells were linearly written to be in a flat file.
"""
import sys
import json
from importlib.machinery import SourceFileLoader

from ipynb.utils import code_from_ipynb, validate_nb
from ipynb.fs.finder import FSFinder


class FullLoader(SourceFileLoader):
    """
    A notebook loader that loads code from a .ipynb file

    It picks out all the code from a .ipynb file and executes it
    into the module.

    If it isn't an .ipnb file, it's treated the same as a .py file
    """
    def get_code(self, fullname):
        if self.path.endswith('.ipynb'):
            with open(self.path) as f:
                try:
                    nb = json.load(f)
                except ValueError:
                    # This is when it isn't a valid json file
                    raise ImportError('Could not import {path} for {fn}: not a valid ipynb file'.format(
                        path=self.path,
                        fn=fullname
                    ))
                if not validate_nb(nb):
                    # This is when it isn't the appropriate
                    # nbformet version or language
                    raise ImportError('Could not import {path} for {fn}: incorrect version or language'.format(
                        path=self.path,
                        fn=fullname
                    ))
                return self.source_to_code(code_from_ipynb(nb), self.path)
        else:
            return super().get_code(fullname)


sys.meta_path.append(FSFinder(__package__, FullLoader))
