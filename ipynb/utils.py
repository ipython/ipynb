"""
Utility functions for dealing with manipulating notebooks.

Try to not put too many things here, nor to re-implement nbformat.
"""
import ast


PREAMBLE=\
"""
##############################################################################
# This source has been auto generated from an IPython/Jupyter notebook file. #
# Please modify the origin file                                              #
##############################################################################
"""

ALLOWED_NODES = set([
    ast.ClassDef,
    ast.FunctionDef,
    ast.Import,
    ast.ImportFrom
])


def validate_nb(nb):
    """
    Validate that given notebook JSON is importable

    - Check for nbformat == 4
    - Check that language is python

    Do not re-implement nbformat here :D
    """
    if nb['nbformat'] != 4:
        return False

    language_name = (nb.get('metadata', {})
        .get('kernelspec', {})
        .get('language', '').lower())
    return language_name == 'python'


def filter_ast(module_ast):
    """
    Filters a given module ast, removing non-whitelisted nodes

    It allows only the following top level items:
     - imports
     - function definitions
     - class definitions
     - top level assignments where all the targets on the LHS are all caps
    """
    def node_predicate(node):
        """
        Return true if given node is whitelisted
        """
        for an in ALLOWED_NODES:
            if isinstance(node, an):
                return True

        # Recurse through Assign node LHS targets when an id is not specified,
        # otherwise check that the id is uppercase
        if isinstance(node, ast.Assign):
            return all([node_predicate(t) for t in node.targets if not hasattr(t, 'id')]) \
                and all([t.id.isupper() for t in node.targets if hasattr(t, 'id')])

        return False

    module_ast.body = [n for n in module_ast.body if node_predicate(n)]
    return module_ast

def code_from_ipynb(nb, markdown=False):
    """
    Get the code for a given notebook

    nb is passed in as a dictionary that's a parsed ipynb file
    """
    code = PREAMBLE
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            # transform the input to executable Python
            code += ''.join(cell['source'])
        if cell['cell_type'] == 'markdown':
            code += '\n# ' + '# '.join(cell['source'])
        # We want a blank newline after each cell's output.
        # And the last line of source doesn't have a newline usually.
        code += '\n\n'
    return code
