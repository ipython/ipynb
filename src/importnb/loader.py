# coding: utf-8
"""# `loader`

Combine the __import__ finder with the loader.
"""

try:
    from .finder import get_loader_details, FuzzySpec, FuzzyFinder
    from .ipython_extension import load_ipython_extension, unload_ipython_extension
    from .decoder import LineCacheNotebookDecoder, quote
    from .docstrings import update_docstring
except:
    from finder import get_loader_details, FuzzySpec, FuzzyFinder
    from ipython_extension import load_ipython_extension, unload_ipython_extension
    from decoder import LineCacheNotebookDecoder, quote
    from docstrings import update_docstring

import ast
import importlib
import inspect
import json
import os
import sys
import textwrap
import types
from contextlib import ExitStack, contextmanager
from functools import partial, partialmethod
from importlib import reload
from importlib.machinery import ModuleSpec, SourceFileLoader
from importlib.util import spec_from_loader
from inspect import signature
from pathlib import Path

_38 = sys.version_info.major == 3 and sys.version_info.minor == 8

if _38:
    from importlib._bootstrap import _load_unlocked, _requires_builtin
else:
    from importlib._bootstrap import _installed_safely, _requires_builtin



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



try:
    import IPython
    from IPython.core.inputsplitter import IPythonInputSplitter

    dedent = IPythonInputSplitter(
        line_input_checker=False,
        physical_line_transforms=[
            IPython.core.inputsplitter.leading_indent(),
            IPython.core.inputsplitter.ipy_prompt(),
            IPython.core.inputsplitter.cellmagic(end_on_blank_line=False),
        ],
    ).transform_cell
except:
    from textwrap import dedent

__all__ = "Notebook", "reload"



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

    finder = FileFinder

    @property
    def loader(self):
        return type(self)

    def __enter__(self):
        id, details = get_loader_details()
        details.insert(self._position, (self.loader, self.extensions))
        sys.path_hooks[id] = self.finder.path_hook(*details)
        sys.path_importer_cache.clear()
        return self

    def __exit__(self, *excepts):
        id, details = get_loader_details()
        details.pop(self._position)
        sys.path_hooks[id] = self.finder.path_hook(*details)
        sys.path_importer_cache.clear()


"""## The basic loader

The loader uses the import systems `get_source`, `get_data`, and `create_module` methods to import notebook files.
"""


class ModuleType(types.ModuleType, getattr(os, "PathLike", object)):
    """ModuleType combines a module with a PathLike access to simplify access."""

    def __fspath__(self):
        return self.__file__


class ImportLibMixin(SourceFileLoader):
    """ImportLibMixin is a SourceFileLoader for loading source code from JSON (e.g. notebooks).
    
    `get_data` assures consistent line numbers between the file s representatio and source."""

    def create_module(self, spec):
        module = ModuleType(spec.name)
        _init_module_attrs(spec, module)
        if isinstance(spec, FuzzySpec):
            sys.modules[spec.alias] = module
        if self.name:
            module.__name__ = self.name
        return module

    def decode(self):
        return decode_source(super().get_data(self.path))

    def get_data(self, path):
        """Needs to return the string source for the module."""
        return LineCacheNotebookDecoder(
            code=self.code, raw=self.raw, markdown=self.markdown
        ).decode(self.decode(), self.path)

    @classmethod
    @_requires_builtin
    def is_package(cls, fullname):
        """Return False as built-in modules are never packages."""
        if "." not in fullname:
            return True
        return super().is_package(fullname)

    get_source = get_data


class NotebookBaseLoader(ImportLibMixin, FinderContextManager):
    """The simplest implementation of a Notebook Source File Loader.
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

    @property
    def loader(self):
        """Create a lazy loader source file loader."""
        loader = super().loader
        if self._lazy and (sys.version_info.major, sys.version_info.minor) != (3, 4):
            loader = LazyLoader.factory(loader)
        # Strip the leading underscore from slots
        return partial(
            loader,
            **{object.lstrip("_"): getattr(self, object) for object in self.__slots__}
        )

    @property
    def finder(self):
        """Permit fuzzy finding of files with special characters."""
        return self._fuzzy and FuzzyFinder or super().finder


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
    def load(cls, filename, dir=None, main=False, **kwargs):
        """Import a notebook as a module from a filename.
        
        dir: The directory to load the file from.
        main: Load the module in the __main__ context.
        
        > assert Notebook.load('loader.ipynb')
        """
        name = main and "__main__" or Path(filename).stem
        loader = cls(name, str(filename), **kwargs)
        spec = FileModuleSpec(name, loader, origin=loader.path)
        module = module_from_spec(spec)
        cwd = str(Path(loader.path).parent)
        try:

            if _38:
                sys.path.append(cwd)
                module = _load_unlocked(spec)
            else:
                with ExitStack() as stack:
                    loader.name != "__main__" and stack.enter_context(
                        _installed_safely(module)
                    )
                    loader.exec_module(module)
        finally:
            sys.path.pop()

        return module


"""* Sometimes folks may want to use the current IPython shell to manage the code and input transformations.
"""

"""Use the `IPythonInputSplitter` to dedent and process magic functions.
"""


class TransformerMixin:
    def code(self, str):
        return dedent(str)

    def markdown(self, str):
        return quote(str)

    def raw(self, str):
        return textwrap.indent(str, "# ")

    def visit(self, node):
        return node


"""## The `Notebook` finder & loader
"""


class Notebook(TransformerMixin, FromFileMixin, NotebookBaseLoader):
    """Notebook is a user friendly file finder and module loader for notebook source code.
    
    > Remember, restart and run all or it didn't happen.
    
    Notebook provides several useful options.
    
    * Lazy module loading.  A module is executed the first time it is used in a script.
    """

    __slots__ = NotebookBaseLoader.__slots__ + ("_main",)

    def __init__(
        self,
        fullname=None,
        path=None,
        lazy=False,
        position=0,
        fuzzy=True,
        markdown_docstring=True,
        main=False,
    ):
        self._main = bool(main) or fullname == "__main__"
        super().__init__(
            self._main and "__main__" or fullname,
            path,
            lazy=lazy,
            fuzzy=fuzzy,
            position=position,
            markdown_docstring=markdown_docstring,
        )

    def parse(self, nodes):
        return ast.parse(nodes, self.path)

    def source_to_code(self, nodes, path, *, _optimize=-1):
        """* Convert the current source to ast 
        * Apply ast transformers.
        * Compile the code."""
        if not isinstance(nodes, ast.Module):
            nodes = self.parse(nodes)
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
