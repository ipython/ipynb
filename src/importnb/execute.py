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
    from .loader import Notebook, lazy_loader_cls
    from .decoder import loads_ast, identity, loads, dedent, cell_to_ast
except:
    from capture import capture_output
    from loader import Notebook, lazy_loader_cls
    from decoder import loads_ast, identity, loads, dedent, cell_to_ast

import inspect, sys, ast
from functools import partialmethod, partial
from importlib import reload, _bootstrap
from traceback import print_exc, format_exc
from warnings import warn
import traceback

__all__ = "Notebook", "Partial", "reload", "Lazy"

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

class Execute(Notebook):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""

    def create_module(self, spec):
        module = super().create_module(spec)
        module.__notebook__ = self._loads(self.get_data(self.path).decode("utf-8"))
        return module

    def _iter_cells(self, module):
        for i, cell in enumerate(module.__notebook__["cells"]):
            if cell["cell_type"] == "code":
                yield self._compile(
                    fix_missing_locations(
                        self.visit(cell_to_ast(cell, transform=self.format, prefix=i > 0))
                    ),
                    self.path or "<notebook-compiled>",
                    "exec",
                )

    def exec_module(self, module, **globals):
        """All exceptions specific in the context.
        """
        module.__dict__.update(globals)
        for cell in module.__notebook__["cells"]:
            if "outputs" in cell:
                cell["outputs"] = []
        for i, code in enumerate(self._iter_cells(module)):
            error = None
            with capture_output(
                stdout=self.stdout, stderr=self.stderr, display=self.display
            ) as out:
                try:
                    _bootstrap._call_with_frames_removed(
                        exec, code, module.__dict__, module.__dict__
                    )
                except BaseException as e:
                    error = new_error(e)
                    print(error)
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

class ParameterizeNode(NodeTransformer):
    visit_Module = NodeTransformer.generic_visit

    def visit_Assign(FreeStatement, node):
        if len(node.targets):
            try:
                if not getattr(node.targets[0], "id", "_").startswith("_"):
                    literal_eval(node.value)
                    return node
            except:
                assert True, """The target can not will not literally evaluate."""
        return None

    def generic_visit(self, node):
        ...

class ExecuteNode(ParameterizeNode):

    def visit_Assign(self, node):
        if super().visit_Assign(node):
            return ast.Expr(Ellipsis())
        return node

    def generic_visit(self, node):
        return node

def vars_to_sig(**vars):
    """Create a signature for a dictionary of names."""
    from inspect import Parameter, Signature

    return Signature([Parameter(str, Parameter.KEYWORD_ONLY, default=vars[str]) for str in vars])

from collections import ChainMap

class Parameterize(Execute, ExecuteNode):

    def create_module(self, spec):
        module = super().create_module(spec)
        nodes = self._data_to_ast(module.__notebook__)
        doc = None
        if isinstance(nodes, ast.Module) and nodes.body:
            node = nodes.body[0]
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                doc = node
        params = ParameterizeNode().visit(nodes)
        doc and params.body.insert(0, doc)
        exec(compile(params, "<parameterize>", "exec"), module.__dict__, module.__dict__)
        return module

    def from_filename(self, filename, path=None, **globals):
        module = super().from_filename(filename, path, exec=False)

        def recall(**kwargs):
            nonlocal module, globals
            module.__loader__.exec_module(module, **ChainMap(kwargs, globals))
            return module

        recall.__signature__ = vars_to_sig(
            **{k: v for k, v in module.__dict__.items() if not k.startswith("_")}
        )
        recall.__doc__ = module.__doc__
        return recall

"""    if __name__ == '__main__':
        f = Parameterize().from_filename('execute.ipynb')
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

"""For more information check out [`importnb`](https://github.com/deathbeds/importnb)
"""

