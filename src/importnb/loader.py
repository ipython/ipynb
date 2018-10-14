# coding: utf-8
"""# `loader`

`loader` is the main module for `importnb`.  It combines with the `finder` to use the Python import system to import notebooks.

Combine the __import__ finder with the loader.

    >>> with Notebook():
    ...      from importnb.notebooks import loader
"""

try:
    from .finder import get_loader_details, FuzzySpec, FuzzyFinder
    from .extensions import load_ipython_extension, unload_ipython_extension
    from .decoder import LineCacheNotebookDecoder
    from .docstrings import update_docstring
except:
    from finder import get_loader_details, FuzzySpec, FuzzyFinder
    from extensions import load_ipython_extension, unload_ipython_extension
    from decoder import LineCacheNotebookDecoder
    from docstrings import update_docstring

import sys, ast, json, inspect, os
from importlib import reload
from importlib.machinery import SourceFileLoader, ModuleSpec
from importlib.util import spec_from_loader
from importlib._bootstrap import _new_module, _installed_safely

from functools import partial

try:
    from importlib._bootstrap_external import decode_source, FileFinder
    from importlib.util import module_from_spec
    from importlib._bootstrap import _init_module_attrs
    from importlib.util import LazyLoader
except:
    # python 3.4
    from importlib._bootstrap import _SpecMethods
    from importlib.util import decode_source
    from importlib.machinery import FileFinder

    def module_from_spec(spec):
        return _SpecMethods(spec).create()

    def _init_module_attrs(spec, module):
        return _SpecMethods(spec).init_module_attrs(module)


from pathlib import Path
from inspect import signature
from contextlib import contextmanager, ExitStack
from functools import partialmethod

__all__ = "Notebook", "reload"

decoder = LineCacheNotebookDecoder()


class FinderContextManager:
    """
    FinderContextManager is the base class for the notebook loader.  It provides
    a context manager that replaces `FileFinder` in the `sys.path_hooks` to include 
    an instance of the class in the python findering system.

    >>> with FinderContextManager() as f:
    ...      id, ((loader_cls, _), *_) = get_loader_details()
    ...      assert issubclass(loader_cls, FinderContextManager)
    >>> id, ((loader_cls, _), *_) = get_loader_details()
    >>> loader_cls = inspect.unwrap(loader_cls)
    >>> assert not (isinstance(loader_cls, type) and issubclass(loader_cls, FinderContextManager))
    """

    extensions = tuple()
    _position = 0

    def __enter__(self):
        id, details = get_loader_details()
        details.insert(self._position, (self.loader_cls(), self.extensions))
        sys.path_hooks[id] = self.finder_cls.path_hook(*details)
        sys.path_importer_cache.clear()
        return self

    def __exit__(self, *excepts):
        id, details = get_loader_details()
        details.pop(self._position)
        sys.path_hooks[id] = self.finder_cls.path_hook(*details)
        sys.path_importer_cache.clear()

    def loader_cls(self):
        return type(self)

    @property
    def finder_cls(self):
        return FileFinder

    @staticmethod
    def _unwrap_loader(loader):
        loader = inspect.unwrap(loader)
        try:
            loader = inspect.getclosurevars(loader).nonlocals.get("loader", loader)
        finally:
            return loader


"""## The basic loader

The loader uses the import systems `get_source`, `get_data`, and `create_module` methods to import notebook files.
"""


class ImportLibMixin:
    def create_module(self, spec):
        module = _new_module(spec.name)
        _init_module_attrs(spec, module)
        if isinstance(spec, FuzzySpec):
            sys.modules[spec.alias] = module
        if self.name:
            module.__name__ = self.name
        return module

    def get_data(self, path):
        return LineCacheNotebookDecoder(code=self.format).decode(
            decode_source(super().get_data(self.path)), self.path
        )

    get_source = get_data


class NotebookBaseLoader(ImportLibMixin, SourceFileLoader, FinderContextManager):
    """The simplest implementation of a Notebook Source File Loader.
    >>> with NotebookBaseLoader():
    ...    from importnb.notebooks import loader
    >>> assert loader.__file__.endswith('.ipynb')
    """

    extensions = (".ipynb",)
    __slots__ = "_lazy", "_fuzzy", "_markdown_docstring", "_position"

    def __init__(
        self,
        fullname=None,
        path=None,
        *,
        lazy=False,
        fuzzy=True,
        position=0,
        markdown_docstring=True
    ):
        super().__init__(fullname, path)
        self._lazy = lazy
        self._fuzzy = fuzzy
        self._markdown_docstring = markdown_docstring
        self._position = position

    def format(self, str):
        return dedent(str)

    def loader_cls(self):
        """Create a lazy loader source file loader."""
        loader = super().loader_cls()
        if self._lazy and (sys.version_info.major, sys.version_info.minor) != (3, 4):
            loader = LazyLoader.factory(loader)
        # Strip the leading underscore from slots
        return partial(
            loader, **{object.lstrip("_"): getattr(self, object) for object in self.__slots__}
        )

    @property
    def finder_cls(self):
        """Permit fuzzy finding of files with special characters."""
        return self._fuzzy and FuzzyFinder or super().finder_cls


class FileModuleSpec(ModuleSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_fileattr = True


"""## notebooks most be loadable from files.
"""


class FromFileMixin:
    """FromFileMixin adds a classmethod to load a notebooks from files.
    """

    @classmethod
    def load(cls, filename, dir=None, shell=True, main=False, **kwargs):
        """Import a notebook as a module from a filename.
        
        dir: The directory to load the file from.
        shell: Use the existing IPython shell.
        main: Load the module in the __main__ context.
        
        > assert Notebook.load('loader.ipynb')
        """
        name = main and "__main__" or Path(filename).stem
        loader = cls(name, str(filename), shell=shell, **kwargs)
        module = module_from_spec(FileModuleSpec(name, loader, origin=loader.path))
        cwd = str(Path(loader.path).parent)
        try:
            with ExitStack() as stack:
                sys.path.append(cwd)
                loader.name != "__main__" and stack.enter_context(_installed_safely(module))
                loader.exec_module(module)
        finally:
            sys.path.pop()

        return module


"""* Sometimes folks may want to use the current IPython shell to manage the code and input transformations.
"""

try:
    from IPython.core.inputsplitter import IPythonInputSplitter

    dedent = IPythonInputSplitter(line_input_checker=False).transform_cell
except:
    from textwrap import dedent


class ShellMixin:
    """ShellMixin allows the current IPython ast and input transformers to be used
    while loading the module."""

    def _get_ipython(self):
        try:
            return __import__("IPython").get_ipython()
        except:
            ...

    def format(self, str):
        shell = self._get_ipython()
        return (
            shell.input_transformer_manager.transform_cell if self._shell and shell else dedent
        )(str)

    def visit(self, node):
        shell = self._get_ipython()
        if self._shell and shell:
            for visitor in shell.ast_transformers:
                node = visitor.visit(node)
        return node


"""## The `Notebook` finder & loader
"""


class Notebook(ShellMixin, FromFileMixin, NotebookBaseLoader):
    """Notebook is a user friendly file finder and module loader for notebook source code.
    
    > Remember, restart and run all or it didn't happen.
    
    Notebook provides several useful options.
    
    * Lazy module loading.  A module is executed the first time it is used in a script.
    """

    __slots__ = NotebookBaseLoader.__slots__ + ("_shell", "_main")

    def __init__(
        self,
        fullname=None,
        path=None,
        lazy=False,
        position=0,
        shell=False,
        fuzzy=True,
        markdown_docstring=True,
        main=False,
    ):
        self._main = bool(main) or fullname == "__main__"
        self._shell = shell
        super().__init__(
            self._main and "__main__" or fullname,
            path,
            lazy=lazy,
            fuzzy=fuzzy,
            position=position,
            markdown_docstring=markdown_docstring,
        )

    def source_to_code(self, nodes, path, *, _optimize=-1):
        """* Convert the current source to ast 
        * Apply ast transformers.
        * Compile the code."""
        if not isinstance(nodes, ast.Module):
            nodes = ast.parse(nodes)
        if self._markdown_docstring:
            nodes = update_docstring(nodes)
        return super().source_to_code(
            ast.fix_missing_locations(self.visit(nodes)), path, _optimize=_optimize
        )


"""# Developer
"""

"""    Notebook.load('loader.ipynb')
    
"""

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("loader.ipynb", "../loader.py")
    print(__import__("doctest").testmod(Notebook.load("loader.ipynb"), verbose=2))
