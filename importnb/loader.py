try:
    from .exporter import Compile, AST
except:
    from exporter import Compile, AST
import inspect, sys
from importlib.machinery import SourceFileLoader
from importlib._bootstrap_external import FileFinder
from importlib import reload
from traceback import print_exc


def update_path_hooks(loader: SourceFileLoader, extensions: tuple = None, lazy=False):
    """Update the FileFinder loader in sys.path_hooks to accomodate a {loader} with the {extensions}"""
    from importlib.util import LazyLoader

    for id, hook in enumerate(sys.path_hooks):
        try:
            closure = inspect.getclosurevars(hook).nonlocals
        except TypeError:
            continue
        if issubclass(closure["cls"], FileFinder):
            sys.path_hooks.pop(id)
            sys.path_hooks.insert(
                id,
                FileFinder.path_hook(
                    *(
                        ((lazy and LazyLoader.factory(loader) or loader, extensions),)
                        if (loader and extensions)
                        else tuple()
                    )
                    + tuple(
                        (cls, ext)
                        for cls, ext in closure["loader_details"]
                        if not issubclass(
                            cls, loader
                        )  # Need to add logic for lazy loaders before they may be introduced.
                    )
                ),
            )
    sys.path_importer_cache.clear()


class ImportContextMixin:

    def __enter__(self):
        update_path_hooks(type(self), self.EXTENSION_SUFFIXES)

    def __exit__(self, exception_type=None, exception_value=None, traceback=None):
        update_path_hooks(type(self))


class Notebook(SourceFileLoader, ImportContextMixin):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""
    EXTENSION_SUFFIXES = ".ipynb",

    def __init__(self, fullname=None, path=None, *, capture=True):
        self.capture = capture
        super().__init__(fullname, path)

    def exec_module(Loader, module):
        try:
            from IPython import get_ipython

            module.get_ipython = get_ipython
        except:
            get_ipython = None

        module.__output__ = None
        if get_ipython and Loader.capture:
            return Loader.exec_module_capture(module)
        else:
            return super().exec_module(module)

    def exec_module_capture(Loader, module):
        from IPython.utils.capture import capture_output

        with capture_output(stdout=False, stderr=False) as output:
            try:
                super().exec_module(module)
            except type("pass", (BaseException,), {}):
                ...
            finally:
                module.__output__ = output
        return module

    def source_to_code(Notebook, data, path):
        with __import__("io").BytesIO(data) as stream:
            return Compile().from_file(stream, filename=Notebook.path, name=Notebook.name)


class Partial(Notebook):

    def exec_module(loader, module):
        try:
            super().exec_module(module)
        except BaseException as exception:
            try:
                raise ImportWarning(
                    """{name} from {file} failed to load completely.""".format(
                        name=module.__name__, file=module.__file__
                    )
                )
            except ImportWarning as error:
                if not loader.capture:
                    print_exc()
                module.__exception__ = exception
        return module


def load_ipython_extension(ip=None):
    Notebook().__enter__()


def unload_ipython_extension(ip=None):
    Notebook().__exit__()


if __name__ == "__main__":
    try:
        from .compiler_python import ScriptExporter
    except:
        from compiler_python import ScriptExporter
    from pathlib import Path

    Path("loader.py").write_text(ScriptExporter().from_filename("loader.ipynb")[0])
    __import__("doctest").testmod()
