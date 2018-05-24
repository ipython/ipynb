# coding: utf-8
'''# The `Execute` importer

The execute importer maintains an attribute that includes the notebooks inputs and outputs.

    >>> import importnb    
    >>> from importnb import notebooks
    >>> with Execute(stdout=True):
    ...      from importnb.notebooks import execute as nb
    
An executed notebook contains a `__notebook__` attributes that is populated with cell outputs.

    >>> assert nb.__notebook__
    
The `__notebook__` attribute complies with `nbformat`

    >>> from nbformat.v4 import new_notebook
    >>> assert new_notebook(**nb.__notebook__), """The notebook is not a valid nbformat"""
    
'''

try:

    from .capture import capture_output
    from .loader import Notebook
    from .decoder import loads_ast, identity, loads, dedent
except:
    from capture import capture_output
    from loader import Notebook
    from decoder import loads_ast, identity, loads, dedent

import inspect, sys, ast
from functools import partialmethod, partial
from importlib import reload, _bootstrap
from traceback import print_exc, format_exc
from warnings import warn
import traceback

__all__ = "Notebook", "Partial", "reload", "Lazy"

def new_stream(text, name="stdout"):
    return {"name": name, "output_type": "stream", "text": text}


def new_error(Exception):
    return {
        "ename": type(Exception).__name__,
        "output_type": "error",
        "evalue": str(Exception),
        "traceback": traceback.format_tb(Exception.__traceback__),
    }


def new_display(object):
    return {"data": object.data, "metadata": {}, "output_type": "display_data"}

def cell_to_ast(object, transform=identity, ast_transform=identity, prefix=False):
    module = ast.increment_lineno(
        ast.parse(transform("".join(object["source"]))), object["metadata"].get("lineno", 1)
    )
    prefix and module.body.insert(0, ast.Expr(ast.Ellipsis()))
    return ast.fix_missing_locations(ast_transform(module))

class Execute(Notebook):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""

    def exec_module(self, module):
        """All exceptions specific in the context.
        """
        module.__notebook__ = self._loads(self.get_data(self.path).decode("utf-8"))
        for cell in module.__notebook__["cells"]:
            if "outputs" in cell:
                cell["outputs"] = []
        for i, cell in enumerate(module.__notebook__["cells"]):
            if cell["cell_type"] == "code":
                error = None
                with capture_output(
                    stdout=self.stdout, stderr=self.stderr, display=self.display
                ) as out:
                    try:
                        code = self._compile(
                            cell_to_ast(
                                cell,
                                transform=self._transform,
                                ast_transform=self._ast_transform,
                                prefix=i > 0,
                            ),
                            self.path or "<notebook-compiled>",
                            "exec",
                        )
                        _bootstrap._call_with_frames_removed(exec, code, module.__dict__)
                    except BaseException as e:
                        error = new_error(e)
                        try:
                            module.__exception__ = e
                            raise e
                        except self._exceptions:
                            ...
                        break
                    finally:
                        if out.outputs:
                            cell["outputs"] += [new_display(object) for object in out.outputs]
                        if out.stdout:
                            cell["outputs"] += [new_stream(out.stdout)]
                        if error:
                            cell["outputs"] += [error]
                        if out.stderr:
                            cell["outputs"] += [new_stream(out.stderr, "stderr")]

"""    if __name__ == '__main__':
        m = Execute(stdout=True).from_filename('loader.ipynb')
"""

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
