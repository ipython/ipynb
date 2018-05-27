# coding: utf-8
if globals().get("show", None):
    print("I am tested.")

try:
    from .capture import capture_output
    from .loader import Notebook, advanced_exec_module, markdown_to_source
    from .decoder import loads_ast, identity, loads, dedent, cell_to_ast
except:
    from capture import capture_output
    from loader import Notebook, advanced_exec_module, markdown_to_source
    from decoder import loads_ast, identity, loads, dedent, cell_to_ast

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

def loader_include_notebook(loader, module):
    module._notebook = loads(loader.get_data(loader.path).decode("utf-8"))

class NotebookCells(Notebook):
    """The NotebookCells loader's contain a _notebook attributes containing a state of the notebook.
    
    >>> assert NotebookCells().from_filename('execute.ipynb', 'importnb.notebooks')._notebook
    """

    @advanced_exec_module
    def exec_module(self, module, **globals):
        loader_include_notebook(self, module)
        _call_with_frames_removed(
            exec, self.source_to_code(module._notebook), module.__dict__, module.__dict__
        )

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

class Execute(Notebook):
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

    @advanced_exec_module
    def exec_module(self, module, **globals):
        # Remove the outputs
        loader_include_notebook(self, module)
        for cell in module._notebook["cells"]:
            if "outputs" in cell:
                cell["outputs"] = []
        for i, cell in enumerate(module._notebook["cells"]):
            error = None
            with capture_output() as out:
                try:
                    if i == 0:
                        cell = markdown_to_source(cell)
                    if cell["cell_type"] == "code":

                        _call_with_frames_removed(
                            exec, self.source_to_code(cell), module.__dict__, module.__dict__
                        )
                except BaseException as Exception:
                    error = new_error(Exception)
                    try:
                        module.__exception__ = Exception
                        raise Exception
                    except self.exceptions:
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
            out.show()

    source_to_code = partialmethod(NotebookCells.source_to_code)

if __name__ == "__main__":
    nb = Execute(display=True, stdout=True).from_filename("execute.ipynb", "importnb.notebooks")

class ParameterizeNode(NodeTransformer):
    """Discover any literal ast expression and create parameters from them. 
    
    >>> assert len(ParameterizeNode().visit(ast.parse('''
    ... foo = 42
    ... bar = foo''')).body) ==1
    """
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

def vars_to_sig(**vars):
    """Create a signature for a dictionary of names."""
    from inspect import Parameter, Signature

    return Signature([Parameter(str, Parameter.KEYWORD_ONLY, default=vars[str]) for str in vars])

class Parameterize(Execute, ParameterizeNode):
    """Discover any literal ast expression and create parameters from them. 
    
    >>> nb = Parameterize().from_filename('execute.ipynb', 'importnb.notebooks')
    >>> assert 'a_variable_to_parameterize' in nb.__signature__.parameters
    
    Parametize is a NodeTransformer that import any nodes return by Parameterize Node.
    
    >>> assert len(Parameterize().visit(ast.parse('''
    ... foo = 42
    ... bar = foo''')).body) ==2
    """

    def visit_Assign(self, node):
        if super().visit_Assign(node):
            return ast.Expr(Ellipsis())
        return node

    def generic_visit(self, node):
        return node

    def create_module(self, spec):
        module = super().create_module(spec)

        # Import the notebook when parameterize is imported
        loader_include_notebook(self, module)

        nodes = self.nb_to_ast(module._notebook)

        # Extra effort to supply a docstring
        doc = None
        if isinstance(nodes, ast.Module) and nodes.body:
            node = nodes.body[0]
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                doc = node

        # Discover the parameterizable nodes
        params = ParameterizeNode().visit(nodes)

        # Include the string in the compilation
        doc and params.body.insert(0, doc)

        # Supply the literal parameter values as module globals.
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

a_variable_to_parameterize = 42

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("execute.ipynb", "../execute.py")
    module = Execute().from_filename("execute.ipynb")
    __import__("doctest").testmod(module, verbose=2)

