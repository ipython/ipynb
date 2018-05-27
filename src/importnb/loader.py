# coding: utf-8
if "show" in globals():
    print("Catch me if you can")

try:
    from .capture import capture_output, CapturedIO
    from .decoder import identity, loads, dedent
    from .path_hooks import PathHooksContext, modify_sys_path, add_path_hooks, remove_one_path_hook
except:
    from capture import capture_output, CapturedIO
    from decoder import identity, loads, dedent
    from path_hooks import PathHooksContext, modify_sys_path, add_path_hooks, remove_one_path_hook

import inspect, sys, ast
from copy import copy
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader

from importlib._bootstrap import _call_with_frames_removed, _new_module

try:
    from importlib._bootstrap import _init_module_attrs, _call_with_frames_removed
    from importlib._bootstrap_external import FileFinder
    from importlib.util import module_from_spec
except:
    # python 3.4
    from importlib.machinery import FileFinder
    from importlib._bootstrap import _SpecMethods

    def module_from_spec(spec):
        return _SpecMethods(spec).create()

    def _init_module_attrs(spec, module):
        return _SpecMethods(spec).init_module_attrs(module)


from io import StringIO
from functools import partialmethod, partial, wraps, singledispatch
from importlib import reload
from traceback import print_exc, format_exc, format_tb
from contextlib import contextmanager, ExitStack
from pathlib import Path

try:
    from importlib.resources import path
except:
    from importlib_resources import path

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

class ImportNbException(BaseException):
    """ImportNbException allows all exceptions to be raised, a null except statement always passes."""

def markdown_to_source(object):
    if object["cell_type"] == "markdown":
        object = copy(object)
        object["source"] = codify_markdown(object["source"])
        object["outputs"] = []
        object["cell_type"] = "code"
        object["execution_count"] = None
    return object

def cell_to_ast(loader, object):
    if object["cell_type"] == "markdown":
        object = markdown_to_source(object)

    if object.get("cell_type", None) in ("code", "markdown"):

        module = ast.increment_lineno(
            ast.parse(loader.format("".join(object["source"]))), object["metadata"].get("lineno", 1)
        )
        return module
    return ast.Module(body=[])

def nb_to_ast(loader, nb):
    return ast.Module(body=sum((loader.cell_to_ast(object).body for object in nb["cells"]), []))

@singledispatch
def codify_markdown(string_or_list):
    raise TypeError("Markdown must be a string or a list.")


@codify_markdown.register(str)
def codify_markdown_string(str):
    if '"""' in str:
        str = "'''{}\n'''".format(str)
    else:
        str = '"""{}\n"""'.format(str)
    return str


@codify_markdown.register(list)
def codify_markdown_list(str):
    return list(map("{}\n".format, codify_markdown_string("".join(str)).splitlines()))

def source_to_code(loader, object, path=None):
    cells = []
    if isinstance(object, bytes):
        object = loads(object.decode("utf-8"))

    if "cells" in object:
        cells.extend(object["cells"])
    elif isinstance(object, dict):
        cells.append(object)
    else:
        cells.append({"source": object, "cell_type": "code"})

    return compile(loader.visit(loader.nb_to_ast({"cells": cells})), path or "<importnb>", "exec")

def from_resource(loader, file=None, resource=None, exec=True, **globals):
    """Load a python module or notebook from a file location.

    from_filename is not reloadable because it is not in the sys.modules.

    This still needs some work for packages.
    
    >> assert from_resource(Notebook(), 'loader.ipynb', 'importnb.notebooks')
    """
    with ExitStack() as stack:
        if resource is not None:
            file = Path(stack.enter_context(path(resource, file)))
        else:
            file = Path(file or loader.path)
        name = (getattr(loader, "name", False) == "__main__" and "__main__") or file.stem
        if file.suffixes[-1] == ".ipynb":
            loader = loader(name, file)
        else:
            loader = SourceFileLoader(name, str(file))

        lazy = getattr(loader, "_lazy", False)
        if lazy:
            try:
                from importlib.util import LazyLoader

                loader = LazyLoader(loader)
            except:
                ImportWarning("""LazyLoading is only available in > Python 3.5""")

        module = module_from_spec(spec_from_loader(name, loader))
        if exec:
            stack.enter_context(modify_sys_path(file))
            module.__loader__.exec_module(module, **globals)
    return module

class NotebookLoader(SourceFileLoader, PathHooksContext):
    """The simplest implementation of a Notebook Source File Loader.
    >>> with NotebookLoader():
    ...    from importnb.notebooks import decoder
    >>> assert decoder.__file__.endswith('.ipynb')
    """
    EXTENSION_SUFFIXES = ".ipynb",

    def __init__(self, fullname=None, path=None):
        super().__init__(fullname, path)

    format = staticmethod(dedent)
    __slots__ = "name", "path",
    source_to_code = source_to_code
    nb_to_ast = nb_to_ast
    cell_to_ast = cell_to_ast

    from_filename = from_resource

    # loader_globals(loader_exceptions(loader_capture()))

    def __call__(self, fullname=None, path=None):
        self = copy(self)
        return SourceFileLoader.__init__(self, str(fullname), str(path)) or self

def advanced_exec_module(exec_module):
    """Decorate `SourceFileLoader.exec_module` objects with abilities to:
    * Capture output in Python and IPython
    * Prepopulate a model namespace.
    * Allow exceptions while notebooks are loading.s
    
    >>> assert advanced_exec_module(SourceFileLoader.exec_module)
    """

    def _exec_module(loader, module, **globals):
        module.__exception__ = None
        module.__dict__.update(globals)
        with capture_output(
            stdout=loader.stdout, stderr=loader.stderr, display=loader.display
        ) as out:
            module._capture = out
            try:
                exec_module(loader, module)
            except loader.exceptions as Exception:
                module._exception = Exception

    return _exec_module

class Notebook(NotebookLoader, ast.NodeTransformer, capture_output):
    """The Notebook loader is an advanced loader for IPython notebooks:
    
    * Capture stdout, stderr, and display objects.
    * Partially evaluate notebook with known exceptions.
    * Supply extra global values into notebooks.
    
    >>> assert Notebook().from_filename('loader.ipynb', 'importnb.notebooks')
    """
    EXTENSION_SUFFIXES = ".ipynb",

    _compile = staticmethod(compile)
    format = _transform = staticmethod(dedent)

    __slots__ = "stdout", "stderr", "display", "_lazy", "exceptions", "globals"

    def __init__(
        self,
        fullname=None,
        path=None,
        *,
        stdout=False,
        stderr=False,
        display=False,
        lazy=False,
        globals=None,
        exceptions=ImportNbException
    ):
        super().__init__(fullname, path)
        capture_output.__init__(self, stdout=stdout, stderr=stderr, display=display)
        self._lazy = lazy
        self.globals = {} if globals is None else globals
        self.exceptions = exceptions

    def create_module(self, spec):
        module = _new_module(spec.name)
        _init_module_attrs(spec, module)
        module.__dict__.update(self.globals)
        return module

    exec_module = advanced_exec_module(NotebookLoader.exec_module)

    def visit(self, node):
        return ast.fix_missing_locations(super().visit(node))

def load_ipython_extension(ip=None):
    add_path_hooks(Notebook, Notebook.EXTENSION_SUFFIXES)


def unload_ipython_extension(ip=None):
    remove_one_path_hook(Notebook)

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("loader.ipynb", "../loader.py")
    m = Notebook().from_filename("loader.ipynb")
    print(__import__("doctest").testmod(m))

