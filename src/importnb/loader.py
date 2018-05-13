try:
    from .exporter import Compile, AST
    from .utils import __IPYTHON__, export
except:
    from exporter import Compile, AST
    from utils import __IPYTHON__, export
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

class ImportContextManagerMixin:
    """A context maanager to add and remove loader_details from the path_hooks.
    """
    def __enter__(self, position=0):  
        add_path_hooks(type(self), self.EXTENSION_SUFFIXES, position=position, lazy=self._lazy)
    def __exit__(self, exception_type=None, exception_value=None, traceback=None): remove_one_path_hook(type(self))

class Notebook(SourceFileLoader, ImportContextManagerMixin):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""
    EXTENSION_SUFFIXES = '.ipynb',

    def __init__(
        self, fullname=None, path=None, *, stdout=False, stderr=False, display=True, lazy=False
    ): 
        self._lazy = lazy
        self._stdout = stdout
        self._stderr = stderr
        self._display = display
        super().__init__(fullname, path)


    @property
    def _capture(self):
        return any((self._stdout, self._stderr, self._display))
    def exec_module(self, module):
        module.__output__ = None
        if __IPYTHON__ and self._capture: 
            return self.exec_module_capture(module)
        else: 
            return super().exec_module(module)

    def exec_module_capture(self, module):
        from IPython.utils.capture import capture_output    
        with capture_output(stdout=self._stdout, stderr=self._stderr, display=self._display) as output: 
            module.__output__= output
            super().exec_module(module)
        return module

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
                if not loader._capture: print_exc()
                module.__exception__ = exception
        return module

def load_ipython_extension(ip=None): Notebook().__enter__(position=0)
def unload_ipython_extension(ip=None): Notebook().__exit__()

if __name__ ==  '__main__':
    export('loader.ipynb', '../importnb/loader.py')
    __import__('doctest').testmod()

