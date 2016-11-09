"""
FileSystem based importer for ipynb / .py files that only imports function / class definitions.
"""
import sys
import ast
import json

from importlib.machinery import SourceFileLoader
from ipynb.fs.finder import FSFinder

from ipynb.utils import get_code, validate_nb


ALLOWED_NODES = set([
    ast.ClassDef,
    ast.FunctionDef,
    ast.Import,
    ast.ImportFrom
])


class NotebookLoader(SourceFileLoader):
    def _filter_ast_node(self, node):
        for an in ALLOWED_NODES:
            if isinstance(node, an):
                return True

        if isinstance(node, ast.Assign):
            return all([t.id.isupper() for t in node.targets])

        return False

    def _get_filtered_ast(self, source):
        """
        Returns an AST from source filtered to contain only our whitelist
        """
        tree = ast.parse(source)
        tree.body = [n for n in tree.body if self._filter_ast_node(n)]
        return tree

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
                    self._get_filtered_ast(get_code(nb)),
                    self.path
                )
        else:
            return super().get_code(fullname)

sys.meta_path.append(FSFinder(__package__, NotebookLoader))
