
# coding: utf-8

"""# The [Import Loader](https://docs.python.org/3/reference/import.html#loaders)

`importnb` uses context manager to import Notebooks as Python packages and modules.  `importnb.Notebook` simplest context manager.  It will find and load any notebook as a module.

    >>> with Notebook(): 
    ...     import importnb
    
The `importnb.Partial` context manager is used when an import raises an error.

    >>> with Partial(): 
    ...     import importnb
    
There is a [lazy importer]()

    >>> with Lazy(): 
    ...     import importnb
    
Loading from a file.

    nb = Untitled = Notebook.from_filename('Untitled.ipynb')
"""


try:
    from .compile import __IPYTHON__, export, Compile, AST
    from .capture import capture_output
except:
    from compile import __IPYTHON__, export, Compile, AST
    from capture import capture_output


import inspect, sys
from importlib.machinery import SourceFileLoader

try:
    from importlib._bootstrap_external import FileFinder
except:
    # python 3.4
    from importlib.machinery import FileFinder

from io import StringIO
from functools import partialmethod, partial
from importlib import reload
from traceback import print_exc, format_exc
from warnings import warn
from contextlib import contextmanager, ExitStack
from pathlib import Path

__all__ = "Notebook", "Partial", "reload", "Lazy"


"""## `sys.path_hook` modifiers
"""


@contextmanager
def modify_file_finder_details():
    """yield the FileFinder in the sys.path_hooks that loads Python files and assure
    the import cache is cleared afterwards.  
    
    Everything goes to shit if the import cache is not cleared."""

    for id, hook in enumerate(sys.path_hooks):
        try:
            closure = inspect.getclosurevars(hook).nonlocals
        except TypeError:
            continue
        if issubclass(closure["cls"], FileFinder):
            sys.path_hooks.pop(id)
            details = list(closure["loader_details"])
            yield details
            break
    sys.path_hooks.insert(id, FileFinder.path_hook(*details))
    sys.path_importer_cache.clear()


"""Update the file_finder details with functions to append and remove the [loader details](https://docs.python.org/3.7/library/importlib.html#importlib.machinery.FileFinder).
"""


def add_path_hooks(loader: SourceFileLoader, extensions, *, position=0, lazy=False):
    """Update the FileFinder loader in sys.path_hooks to accomodate a {loader} with the {extensions}"""
    with modify_file_finder_details() as details:
        try:
            from importlib.util import LazyLoader

            if lazy:
                loader = LazyLoader.factory(loader)
        except:
            ImportWarning("""LazyLoading is only available in > Python 3.5""")
        details.insert(position, (loader, extensions))


def remove_one_path_hook(loader):
    with modify_file_finder_details() as details:
        _details = list(details)
        for ct, (cls, ext) in enumerate(_details):
            cls = lazy_loader_cls(cls)
            if issubclass(cls, loader):
                details.pop(ct)
                break


def lazy_loader_cls(loader):
    """Extract the loader contents of a lazy loader in the import path."""
    if not isinstance(loader, type) and callable(loader):
        return inspect.getclosurevars(loader).nonlocals.get("cls", loader)
    return loader


"""## Context Manager

`importnb` uses a context manager to assure that the traditional import system behaviors as expected.  If the loader is permenantly available then it may create some unexpected import behaviors.
"""


"""The way the context manager works it is difficult to attach contexts to each module.
"""


class ImportNbException(BaseException):
    """ImportNbException allows all exceptions to be raised, a null except statement always passes."""


class Notebook(SourceFileLoader, capture_output):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""
    EXTENSION_SUFFIXES = ".ipynb",

    def __init__(
        self,
        fullname=None,
        path=None,
        *,
        stdout=False,
        stderr=False,
        display=False,
        lazy=False,
        exceptions=None
    ):
        path = str(path)
        SourceFileLoader.__init__(self, fullname, path)
        capture_output.__init__(self, stdout=stdout, stderr=stderr, display=display)
        self._lazy = lazy
        self._exceptions = exceptions or ImportNbException

    def __enter__(self, position=0):
        add_path_hooks(type(self), self.EXTENSION_SUFFIXES, position=position, lazy=self._lazy)
        return super().__enter__()

    def exec_module(self, module):
        """All exceptions specific in the context."""
        module.__doc__ = module.__doc__ or ""
        try:
            super().exec_module(module)
            module.__exception__ = None
        except self._exceptions as e:
            """Display a message if an error is escaped."""
            module.__exception__ = e
            warn(
                ".".join(
                    [
                        """{name} was partially imported with a {error}""".format(
                            error=type(e), name=module.__name__
                        ),
                        "=" * 10,
                        format_exc(),
                    ]
                )
            )

    def __exit__(self, *excepts):
        remove_one_path_hook(type(self)), super().__exit__(*excepts)

    def source_to_code(Notebook, data, path):
        with StringIO(data.decode("utf-8")) as stream:
            return Compile().from_file(stream, filename=Notebook.path, name=Notebook.name)

    def from_filename(self, file):
        """Load a python module or notebook from a file location.

        from_filename is not reloadable because it is not in the sys.modules.

        This still needs some work for packages.
        """
        from importlib.util import spec_from_loader

        try:
            from importlib.util import module_from_spec
        except:
            # Python 3.4 compatability
            from importlib._bootstrap import _SpecMethods

            def module_from_spec(spec):
                return _SpecMethods(spec).create()

        file = Path(file)
        name = (self.name == "__main__" and "__main__") or file.stem

        if file.suffixes[-1] == ".ipynb":
            loader = self
            loader.name = name
            loader.path = str(file)
        else:
            loader = SourceFileLoader(name, str(file))

        with capture_output(self.stdout, self.stderr, self.display) as captured:
            spec = spec_from_loader(name, loader)
            module = module_from_spec(spec)
            module.__loader__.exec_module(module)

        module.__output__ = captured
        return module

    __call__ = from_filename


"""### Partial Loader
"""


class Partial(Notebook):
    """A partial import tool for notebooks.
    
    Sometimes notebooks don't work, but there may be useful code!
    
    with Partial():
        import Untitled as nb
        assert nb.__exception__
    
    if isinstance(nb.__exception__, AssertionError):
        print("There was a False assertion.")
            
    Partial is useful in logging specific debugging approaches to the exception.
    """
    __init__ = partialmethod(Notebook.__init__, exceptions=BaseException)


"""### Lazy Loader

The lazy loader is helpful for time consuming operations.  The module is not evaluated until it is used the first time after loading.
"""


class Lazy(Notebook):
    """A lazy importer for notebooks.  For long operations and a lot of data, the lazy importer delays imports until 
    an attribute is accessed the first time.
    
    with Lazy():
        import Untitled as nb
    """
    __init__ = partialmethod(Notebook.__init__, lazy=True)


"""# IPython Extensions
"""


def load_ipython_extension(ip=None):
    add_path_hooks(Notebook, Notebook.EXTENSION_SUFFIXES)


def unload_ipython_extension(ip=None):
    remove_one_path_hook(Notebook)


"""# Developer
"""


if __name__ == "__main__":
    export("loader.ipynb", "../importnb/loader.py")
    __import__("doctest").testmod(Notebook()("loader.ipynb"))
