"""
FileSystem based importer for ipynb / .py files that only imports function / class definitions.
"""
import sys
import ast

from importlib.machinery import SourceFileLoader
from ipynb.fs.finder import FSFinder

from ipynb.utils import get_code


ALLOWED_NODES = set([
    ast.ClassDef,
    ast.FunctionDef,
    ast.Import,
    ast.ImportFrom
])


class NotebookLoader(SourceFileLoader):
    def _get_filtered_ast(self, source):
        """
        Returns an AST from source filtered to contain only our whitelist
        """
        tree = ast.parse(source)
        tree.body = [
            node for node in tree.body
            if type(node) in ALLOWED_NODES
        ]
        return tree

    def get_code(self, fullname):
        if self.path.endswith('.ipynb'):
            with open(self.path) as f:
                return compile(
                    self._get_filtered_ast(get_code(f.read())),
                    self.path,
                    'exec'
                )
        else:
            return super().get_code(fullname)

sys.meta_path.append(FSFinder(__package__, NotebookLoader))
