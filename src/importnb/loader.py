try:
    from .exporter import Compile, AST
    from .utils import __IPYTHON__, export
    from .capture import capture_output
except:
    from exporter import Compile, AST
    from utils import __IPYTHON__, export
    from capture import capture_output
import inspect, sys
from importlib.machinery import SourceFileLoader
try: 
    from importlib._bootstrap_external import FileFinder
except:
    #python 3.4
    from importlib.machinery import FileFinder
from importlib import reload
from traceback import print_exc
from contextlib import contextmanager

__all__ = 'Notebook', 'Partial', 'reload',

@contextmanager
def modify_file_finder_details():
    """yield the FileFinder in the sys.path_hooks that loads Python files and assure
    the import cache is cleared afterwards.  

    Everything goes to shit if the import cache is not cleared."""

    for id, hook in enumerate(sys.path_hooks):
        try:
            closure = inspect.getclosurevars(hook).nonlocals
        except TypeError: continue
        if issubclass(closure['cls'], FileFinder):
            sys.path_hooks.pop(id)
            details = list(closure['loader_details'])
            yield details
            break
    sys.path_hooks.insert(id, FileFinder.path_hook(*details))
    sys.path_importer_cache.clear()

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
        return inspect.getclosurevars(loader).nonlocals.get('cls', loader)
    return loader

from contextlib import ExitStack

class Notebook(SourceFileLoader, ExitStack):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""
    EXTENSION_SUFFIXES = '.ipynb',

    def __init__(
        self, fullname=None, path=None, *, stdout=False, stderr=False, display=True, lazy=False
    ): 
        SourceFileLoader.__init__(self, fullname, path)
        ExitStack.__init__(self)
        self._stdout, self._stderr, self._display = stdout, stderr, display
        self._lazy = lazy

    def __enter__(self, position=0):  
        add_path_hooks(type(self), self.EXTENSION_SUFFIXES, position=position, lazy=self._lazy)
        stack = super().__enter__()
        return stack.enter_context(capture_output(
            stdout=self._stdout, stderr=self._stderr, display=self._display
        ))

    def __exit__(self, *excepts):  remove_one_path_hook(type(self))

    def exec_module(self, module): super().exec_module(module)                

    def source_to_code(Notebook, data, path):
        with __import__('io').BytesIO(data) as stream:
            return Compile().from_file(stream, filename=Notebook.path, name=Notebook.name)

class Partial(Notebook):
    def exec_module(loader, module):
        try: super().exec_module(module)
        except BaseException as exception:
            try: 
                raise ImportWarning("""{name} from {file} failed to load completely.""".format(
                    name=module.__name__, file=module.__file__
                ))
            except ImportWarning as error:
                if not loader._stderr: print_exc()
                module.__exception__ = exception
        return module

def load_ipython_extension(ip=None): 
    add_path_hooks(Notebook, Notebook.EXTENSION_SUFFIXES)
def unload_ipython_extension(ip=None): 
    remove_one_path_hook(Notebook)

if __name__ ==  '__main__':
    export('loader.ipynb', '../importnb/loader.py')
    __import__('doctest').testmod()