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

    @advanced_exec_module
    def exec_module(self, module, **globals):
        loader_include_notebook(self, module)
        for i, cell in enumerate(module._notebook["cells"]):
            if module._exception:
                break
            self.exec_cell(module, cell, index=i)

    def exec_cell(self, module, cell, index=0):
        """Returns an error if there was one."""
        _call_with_frames_removed(
            exec,
            self.source_to_code(cell, interactive=bool(index)),
            module.__dict__,
            module.__dict__,
        )

    def visit_Module(self, node):
        return ast.Interactive(body=super().visit_Module(node).body)

    def source_to_code(loader, cell, path=None, interactive=True):
        """Transform ast modules into Interactive and Expression nodes. This 
            will allow the cell outputs to be captured.  `interactive` is only true for
            the first markdown cell.
            """

        node = loader.visit(cell)

        if isinstance(node, ast.Expr):
            node = ast.Expression(body=node.value) if interactive else ast.Module(body=[node])

        if isinstance(node, ast.Expression):
            mode = "eval"
        if isinstance(node, ast.Interactive):
            mode = "single"
        if isinstance(node, ast.Module):
            mode = "exec"

        return compile(node, path or "<importnb>", mode)


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

    @advanced_exec_module
    def exec_module(self, module):
        loader_include_notebook(self, module)
        for cell in module._notebook["cells"]:
            if "outputs" in cell:
                cell["outputs"] = []
        super().exec_module(module)

    def exec_cell(self, module, cell, index=0):
        error = None
        with capture_output() as out:
            exception = super().exec_cell(module, cell, index=index)
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
    nb = Execute(display=True).from_filename("execute.ipynb", "importnb.notebooks")

"""# Parameterizing notebooks
"""


class AssignmentFinder(NodeTransformer):
    visit_Interactive = visit_Module = NodeTransformer.generic_visit

    def visit_Assign(self, node):
        if len(node.targets):
            try:
                if not getattr(node.targets[0], "id", "_").startswith("_"):
                    literal_eval(node.value)
                    return node
            except:
                ...

    def generic_visit(self, node):
        ...


class AssignmentIgnore(AssignmentFinder):

    def visit_Assign(self, node):
        if isinstance(super().visit_Assign(node), ast.Assign):
            return ast.Expr(ast.NameConstant(value=None))
        return node

    generic_visit = Execute.generic_visit


def copy_module(module):
    new = type(module)(module.__name__)
    new.__dict__.update(module.__dict__)
    return new


class Parameterize(Execute):
    """Discover any literal ast expression and create parameters from them. 
    
    >>> f = Parameterize().from_filename('execute.ipynb', 'importnb.notebooks')
    >>> assert 'a_variable_to_parameterize' in f.__signature__.parameters
    >>> assert f(a_variable_to_parameterize=100).a_variable_to_parameterize == 100
    
    Parametize is a NodeTransformer that import any nodes return by Parameterize Node.
    
    >>> assert len(Parameterize().visit(ast.parse('''
    ... foo = 42
    ... bar = foo''')).body) ==2
    """

    def create_module(self, spec):
        module = super().create_module(spec)

        # Import the notebook when parameterize is imported
        loader_include_notebook(self, module)

        node = Notebook().visit(module._notebook)

        # Extra effort to supply a docstring
        doc = None
        if isinstance(node, ast.Module) and node.body:
            _node = node.body[0]
            if isinstance(_node, ast.Expr) and isinstance(_node.value, ast.Str):
                doc = _node

            # Discover the parameterizable nodes
        params = AssignmentFinder().visit(node)
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
            return copy_module(module)

        recall.__signature__ = vars_to_sig(
            **{k: v for k, v in module.__dict__.items() if not k.startswith("_")}
        )
        recall.__doc__ = module.__doc__
        return recall

    def visit(self, node):
        return AssignmentIgnore().visit(super().visit(node))


def vars_to_sig(**vars):
    """Create a signature for a dictionary of names."""
    from inspect import Parameter, Signature

    return Signature([Parameter(str, Parameter.KEYWORD_ONLY, default=vars[str]) for str in vars])


if __name__ == "__main__":
    f = Parameterize(exceptions=BaseException).from_filename("execute.ipynb", "importnb.notebooks")
    m = f(a_variable_to_parameterize=1000)

a_variable_to_parameterize = 42

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

"""How do the interactive nodes work?
"""
