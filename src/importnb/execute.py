# coding: utf-8
'''# The `Execute` importer

`Interactive` and `Execute` contain the notebook as an object.  The execute importer maintains an attribute that includes the notebooks inputs and outputs.

    >>> import importnb    
    >>> with Execute(stdout=True):
    ...     from importnb.notebooks import execute as nb
    
An executed notebook contains a `__notebook__` attributes that is populated with cell outputs.

    >>> assert nb._notebook
    
The `__notebook__` attribute complies with `nbformat`

    >>> from nbformat.v4 import new_notebook
    >>> assert new_notebook(**nb._notebook), """The notebook is not a valid nbformat"""
    
'''

if globals().get("show", None):
    print("I am tested.")

from .capture import capture_output
from .loader import Notebook, advanced_exec_module, reload, loads

import ast
from importlib._bootstrap import _call_with_frames_removed

from traceback import format_tb

__all__ = "Interactive", "Execute"

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


def new_display(object, metadata=None):
    if isinstance(object, tuple):
        """It came from a repr_mimebundle"""
        object.metadata = object[0], metadata
    object = getattr(object, "data", object)

    return {"data": object, "metadata": metadata or {}, "output_type": "display_data"}


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

        >>> nb_raw = Notebook(display=True, stdout=True, shell=True).from_filename('execute.ipynb', 'importnb.notebooks')
        >>> with Execute(display=True, stdout=True, shell=True) as loader:
        ...    nb = loader.from_filename('execute.ipynb', 'importnb.notebooks', show=True)

        The loader includes the first markdown cell or leading block string as the docstring.

        >>> assert nb.__doc__ and nb_raw.__doc__ 
        >>> assert nb.__doc__ == nb_raw.__doc__

        Nothing should have been executed.

        >>> assert any(cell.get('outputs', None) for cell in nb._notebook['cells'])        
        """

    def _exec_cell(self, cell, node, module, prev=None):
        if cell["cell_type"] == "markdown":
            if prev is None:
                self._call_exec(node, module)
                node.body.clear()
                return cell, node

        _cell, _node = prev or ({}, ast.Module())

        if cell["cell_type"] == "markdown":
            """Leading markdown class/function cells become the docstring"""
            if getattr(_node, "body", False) and _cell.get("cell_type", None) == "markdown":
                self._call_exec(ast.Expression(_node.body[0].value), module)

        if cell["cell_type"] == "code":
            if _cell.get("cell_type", None) == "markdown":
                if (
                    getattr(node, "body", [])
                    and isinstance(node.body[0], (ast.ClassDef, ast.FunctionDef))
                    and ast.get_docstring(node.body[0]) is None
                ):
                    """Make a leading markdown cell the docstring"""
                    node.body[0].body.insert(0, _node.body[0])
            # This is where we could assign function and class docstrings
            for expression in node.body:
                """Evaluate one node at a time."""
                if expression == node.body[-1]:
                    """The last node is interactive."""
                    if hasattr(expression, "body"):
                        expression = ast.Module([expression])
                    else:
                        expression = ast.Interactive(body=[expression])
                else:
                    """Execute Expr as Expressions so the docstring doesn't change."""
                    if isinstance(expression, ast.Expr):
                        expression = ast.Expression(expression.value)
                    else:
                        """Everything else must a module."""
                        expression = ast.Module([expression])
                self._call_exec(expression, module)
        return cell, node

    def _call_exec(self, expression, module):
        _call_with_frames_removed(
            exec,
            compile(expression, module.__name__, exec_modes(expression)),
            module.__dict__,
            module.__dict__,
        )

    def set_notebook(self, module):
        module._notebook = loads(self.get_data(self.path).decode("utf-8"))

    @advanced_exec_module
    def exec_module(self, module, **globals):
        self.set_notebook(module)
        prev = None
        for cell, node in self._iter_cells(module._notebook):
            if module._exception:
                break

            self._exec_cell(cell, node, module, prev=prev)
            prev = cell, node


if __name__ == "__main__":
    nb = Interactive(shell=True).from_filename("execute.ipynb", "importnb.notebooks")


class Execute(Interactive):
    """The Execute loader reproduces outputs in the module._notebook attribute.

    >>> nb_raw = Notebook(display=True, stdout=True, shell=True).from_filename('execute.ipynb', 'importnb.notebooks')
    >>> with Execute(display=True, stdout=True, shell=True) as loader:
    ...    nb = loader.from_filename('execute.ipynb', 'importnb.notebooks', show=True)
    
    The loader includes the first markdown cell or leading block string as the docstring.
    
    >>> assert nb.__doc__ and nb_raw.__doc__ 
    >>> assert nb.__doc__ == nb_raw.__doc__

    Nothing should have been executed.
    
    >>> assert any(cell.get('outputs', None) for cell in nb._notebook['cells'])        
    """

    def _exec_cell(self, cell, node, module, prev=None):
        error = None
        with capture_output() as out:
            super()._exec_cell(cell, node, module, prev=prev)
        out._outputs = [
            dict(zip(("data", "metadata"), object)) if isinstance(object, tuple) else object
            for object in out._outputs
        ]

        if "outputs" in cell:
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
    nb = Execute(display=True, shell=True).from_filename("execute.ipynb", "importnb.notebooks")


class f:
    a = 10


"""# Developer
"""

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("execute.ipynb", "../execute.py")
    module = Execute(shell=True).from_filename("execute.ipynb")
    __import__("doctest").testmod(module, verbose=2)
