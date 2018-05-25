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

    loader = Notebook()
    nb = Untitled = loader.from_filename('Untitled.ipynb')
    nb = Untitled = loader('Untitled.ipynb')
"""

try:
    from .capture import capture_output
    from .decoder import identity, loads, dedent, cell_to_ast
except:
    from capture import capture_output
    from decoder import identity, loads, dedent, cell_to_ast

import inspect, sys
from copy import copy
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader

try:
    from importlib._bootstrap import _init_module_attrs
    from importlib._bootstrap_external import FileFinder
    from importlib.util import module_from_spec
except:
    # python 3.4
    from importlib.machinery import FileFinder
    from importlib._bootstrap import _SpecMethods

    def module_from_spec(spec):
        return _SpecMethods(spec).create()

    def _init_module_attrs(module):
        return _SpecMethods(module.__spec__).init_module_attrs(module)


from io import StringIO
from functools import partialmethod, partial
from importlib import reload, _bootstrap
from traceback import print_exc, format_exc
from warnings import warn
from contextlib import contextmanager, ExitStack
from pathlib import Path

try:
    from importlib.resources import path
except:
    from importlib_resources import path

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

def add_path_hooks(loader: SourceFileLoader, extensions, *, position=0):
    """Update the FileFinder loader in sys.path_hooks to accomodate a {loader} with the {extensions}"""
    with modify_file_finder_details() as details:
        details.insert(position, (loader, extensions))


def remove_one_path_hook(loader):
    loader = lazy_loader_cls(loader)
    with modify_file_finder_details() as details:
        _details = list(details)
        for ct, (cls, ext) in enumerate(_details):
            cls = lazy_loader_cls(cls)
            if cls == loader:
                details.pop(ct)
                break

def lazy_loader_cls(loader):
    """Extract the loader contents of a lazy loader in the import path."""
    try:
        return inspect.getclosurevars(loader).nonlocals.get("cls", loader)
    except:
        return loader

"""## Loader Context Manager

`importnb` uses a context manager to assure that the traditional import system behaviors as expected.  If the loader is permenantly available then it may create some unexpected import behaviors.
"""

class ImportNbException(BaseException):
    """ImportNbException allows all exceptions to be raised, a null except statement always passes."""

class PathHooksContext:

    def __enter__(self, position=0):
        add_path_hooks(self.prepare(self), self.EXTENSION_SUFFIXES, position=position)
        return self

    def __exit__(self, *excepts):
        remove_one_path_hook(self)

    def prepare(self, loader):
        if self._lazy:
            try:
                from importlib.util import LazyLoader

                if self._lazy:
                    loader = LazyLoader.factory(loader)
            except:
                ImportWarning("""LazyLoading is only available in > Python 3.5""")
        return loader

def from_resource(loader, file=None, resource=None):
    """Load a python module or notebook from a file location.

    from_filename is not reloadable because it is not in the sys.modules.

    This still needs some work for packages.
    
    >>> assert from_resource(Notebook(), 'loader.ipynb', 'importnb.notebooks')
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

        if getattr(loader, "_lazy", False):
            try:
                from importlib.util import LazyLoader

                loader = LazyLoader(loader)
            except:
                ImportWarning("""LazyLoading is only available in > Python 3.5""")

        module = module_from_spec(spec_from_loader(name, loader))
        stack.enter_context(modify_sys_path(file))
        module.__loader__.exec_module(module)

    return module

@contextmanager
def modify_sys_path(file):
    """This is only invoked when using from_resource."""
    path = str(Path(file).parent)
    if path not in map(str, map(Path, sys.path)):
        yield sys.path.insert(0, path)
        sys.path = [object for object in sys.path if str(Path(object)) != path]
    else:
        yield

class Notebook(SourceFileLoader, PathHooksContext, capture_output):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""
    EXTENSION_SUFFIXES = ".ipynb",

    _compile = staticmethod(compile)
    _loads = staticmethod(loads)
    _transform = staticmethod(dedent)
    _ast_transform = staticmethod(identity)

    __slots__ = "stdout", "stderr", "display", "_lazy", "_exceptions"

    def __init__(
        self,
        fullname=None,
        path=None,
        *,
        stdout=False,
        stderr=False,
        display=False,
        lazy=False,
        exceptions=ImportNbException,
        globals=None
    ):
        SourceFileLoader.__init__(self, fullname, path)
        capture_output.__init__(self, stdout=stdout, stderr=stderr, display=display)
        self._lazy = lazy
        self._exceptions = exceptions
        self.globals = {} if globals is None else globals

    def __call__(self, fullname=None, path=None):
        self = copy(self)
        return SourceFileLoader.__init__(self, str(fullname), str(path)) or self

    def create_module(self, spec):
        module = _bootstrap._new_module(spec.name)
        module = _bootstrap._init_module_attrs(spec, module)
        module.__exception__ = None
        module.__dict__.update(self.globals)
        return module

    def exec_module(self, module):
        """All exceptions specific in the context.
        """
        with capture_output(stdout=self.stdout, stderr=self.stderr, display=self.display) as out:
            module.__output__ = out
            try:
                super().exec_module(module)
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

    def source_to_code(self, data, path):
        import ast

        module = ast.Module(body=[])
        module.body = sum(
            (
                cell_to_ast(
                    object, transform=self._transform, ast_transform=self._ast_transform
                ).body
                for object in self._loads(data.decode("utf-8"))["cells"]
            ),
            module.body,
        )
        return self._compile(module, path or "<notebook-compiled>", "exec")

    from_filename = from_resource

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

def main(*files):
    with ExitStack() as stack:
        loader = stack.enter_context(Notebook("__main__"))
        if not files:
            files = sys.argv[1:]
        for file in files:
            loader.from_filename(file)

"""# Developer
"""

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("loader.ipynb", "../loader.py")
    __import__("doctest").testmod(Notebook().from_filename("loader.ipynb"), verbose=2)

"""    if __name__ ==  '__main__':
        __import__('doctest').testmod(Notebook().from_filename('loader.ipynb'), verbose=2)
"""

