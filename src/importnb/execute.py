# coding: utf-8
'''# The `Execute` importer

The execute importer maintains an attribute that includes the notebooks inputs and outputs.

    >>> import importnb    
    >>> from importnb import notebooks
    >>> with Execute(stdout=True):
    ...      from importnb.notebooks import execute as nb
    
An executed notebook contains a `__notebook__` attributes that is populated with cell outputs.

    >>> assert nb._notebook
    
The `__notebook__` attribute complies with `nbformat`

    >>> from nbformat.v4 import new_notebook
    >>> assert new_notebook(**nb._notebook), """The notebook is not a valid nbformat"""
    
'''

if globals().get("show", None):
    print("I am tested.")

try:
    from .capture import capture_output
    from .loader import Notebook, advanced_exec_module
    from .decoder import identity, loads, dedent
except:
    from capture import capture_output
    from loader import Notebook, advanced_exec_module
    from decoder import identity, loads, dedent

import inspect, sys, ast
from functools import partialmethod, partial
from importlib import reload, _bootstrap
from importlib._bootstrap import _call_with_frames_removed, _new_module

import traceback
from traceback import print_exc, format_exc, format_tb
from pathlib import Path

from ast import (
    NodeTransformer,
    parse,
    Assign,
    literal_eval,
    dump,
    fix_missing_locations,
    Str,
    Tuple,
    Ellipsis,
    Interactive,
)
from collections import ChainMap

__all__ = "Notebook", "Partial", "reload", "Lazy"

"""# Loaders that reproduce notebook outputs
"""


def loader_include_notebook(loader, module):
    if not hasattr(module, "_notebook"):
        module._notebook = loads(loader.get_data(loader.path).decode("utf-8"))


"""## Recreating IPython output objectss
"""


def new_stream(text, name="stdout"):
    return {"name": name, "output_type": "stream", "text": text}


def new_error(Exception):
    return {
        "ename": type(Exception).__name__,
        "output_type": "error",
        "evalue": str(Exception),
        "traceback": format_tb(Exception.__traceback__),
    }


def new_display(object):
    return {"data": object.data, "metadata": {}, "output_type": "display_data"}


"""# Reproduce notebooks with the `Execute` class.
"""


def exec_modes(node):
    if isinstance(node, ast.Module):
        return "exec"
    if isinstance(node, ast.Expression):
        return "eval"
    if isinstance(node, ast.Interactive):
        return "single"


class Interactive(Notebook):
    """The Execute loader reproduces outputs in the module._notebook attribute.

        >>> nb_raw = Notebook(display=True, stdout=True).from_filename('execute.ipynb', 'importnb.notebooks')
        >>> with Execute(display=True, stdout=True) as loader:
        ...    nb = loader.from_filename('execute.ipynb', 'importnb.notebooks', show=True)

        The loader includes the first markdown cell or leading block string as the docstring.

        >>> assert nb.__doc__ and nb_raw.__doc__ 
        >>> assert nb.__doc__ == nb_raw.__doc__

        Nothing should have been executed.

        >>> assert any(cell.get('outputs', None) for cell in nb._notebook['cells'])        
        """

    def _exec_cell(self, cell, node, module, index=0):
        node_ct = 0
        while node.body:
            expression = node.body.pop(0)
            if node_ct == index == 0 and cell["cell_type"] == "markdown":
                expression = ast.Module([expression])
            else:
                if not node.body:
                    expression = ast.Interactive([expression])
                else:
                    if isinstance(expression, ast.Expr):
                        expression = ast.Expression(expression.value)
                    else:
                        expression = ast.Module([expression])

            _call_with_frames_removed(
                exec,
                compile(expression, module.__name__, exec_modes(expression)),
                module.__dict__,
                module.__dict__,
            )

            node_ct += 1

    @advanced_exec_module
    def exec_module(self, module, **globals):
        loader_include_notebook(self, module)
        for index, (cell, node) in enumerate(self._iter_cells(module._notebook)):
            if module._exception:
                break
            self._exec_cell(cell, node, module, index=index)


if __name__ == "__main__":
    nb = Interactive(exceptions=BaseException).from_filename("execute.ipynb", "importnb.notebooks")


class Execute(Interactive):
    """The Execute loader reproduces outputs in the module._notebook attribute.

    >>> nb_raw = Notebook(display=True, stdout=True).from_filename('execute.ipynb', 'importnb.notebooks')
    >>> with Execute(display=True, stdout=True) as loader:
    ...    nb = loader.from_filename('execute.ipynb', 'importnb.notebooks', show=True)
    
    The loader includes the first markdown cell or leading block string as the docstring.
    
    >>> assert nb.__doc__ and nb_raw.__doc__ 
    >>> assert nb.__doc__ == nb_raw.__doc__

    Nothing should have been executed.
    
    >>> assert any(cell.get('outputs', None) for cell in nb._notebook['cells'])        
    """

    def _exec_cell(self, cell, node, module, index=0):
        error = None
        with capture_output() as out:
            super()._exec_cell(cell, node, module, index)
            if out.outputs:
                cell["outputs"] += [new_display(object) for object in out.outputs]
            if out.stdout:
                cell["outputs"] += [new_stream(out.stdout)]
            if error:
                cell["outputs"] += [error]
            if out.stderr:
                cell["outputs"] += [new_stream(out.stderr, "stderr")]
        out.show()


if __name__ == "__main__":
    nb = Execute(display=False).from_filename("execute.ipynb", "importnb.notebooks")

"""# Developer
"""

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("execute.ipynb", "../execute.py")
    module = Execute().from_filename("execute.ipynb")
    __import__("doctest").testmod(module, verbose=2)
