"""
FileSystem based importer for ipynb / .py files that only imports function / class definitions.
"""
import sys
import ast
import json

from importlib.machinery import SourceFileLoader
from ipynb.fs.finder import FSFinder

from ipynb.utils import code_from_ipynb, validate_nb, filter_ast



class FilteredLoader(SourceFileLoader):
    """
    A notebook loader that loads only a subset of the code in an .ipynb file

    It executes and imports only the following top level items:
     - imports
     - function definitions
     - class definitions
     - top level assignments where all the targets on the LHS are all caps

    If it isn't an .ipynb file, it's treated the same as a .py file.
    """
    def get_code(self, fullname):
        if self.path.endswith('.ipynb'):
            with open(self.path) as f:
                nb = json.load(f)
                if not validate_nb(nb):
                    raise ImportError('Could not import {path} for {fn}: not a valid ipynb file'.format(
                        path=self.path,
                        fn=fullname
                    ))
                return self.source_to_code(
                    filter_ast(ast.parse(code_from_ipynb(nb))),
                    self.path
                )
        else:
            return super().get_code(fullname)

sys.meta_path.append(FSFinder(__package__, FilteredLoader))
