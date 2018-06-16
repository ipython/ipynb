# coding: utf-8
"""# `sys.path_hook` modifiers

Many suggestions for importing notebooks use `sys.meta_paths`, but `importnb` relies on the `sys.path_hooks` to load any notebook in the path. `PathHooksContext` is a base class for the `importnb.Notebook` `SourceFileLoader`.
"""

from .capture import capture_output, CapturedIO

import inspect, sys, ast, os
from pathlib import Path

try:
    from importlib._bootstrap_external import FileFinder as _FileFinder
except:
    # python 3.4
    from importlib.machinery import FileFinder as _FileFinder

from contextlib import contextmanager, ExitStack

from itertools import chain


class FileFinder(_FileFinder):
    """Adds the ability to open file names with special characters using underscores."""

    def find_spec(self, fullname, target=None):
        """Try to finder the spec and if it cannot be found, use the underscore starring syntax
        to identify potential matches.
        """
        spec = super().find_spec(fullname, target=target)

        if spec is None:
            original = fullname

            if "." in fullname:
                original, fullname = fullname.rsplit(".", 1)
            else:
                original, fullname = "", original

            if "_" in fullname:
                files = chain(
                    Path(self.path).glob(fullname + ".*"),
                    Path(self.path).glob(
                        fullname.replace("__", "*").replace("_", "?").__add__(".*")
                    ),
                )

                try:
                    spec = super().find_spec(
                        (original + "." + next(files).stem).lstrip("."), target=target
                    )
                except StopIteration:
                    ...

        return spec


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
        if issubclass(closure["cls"], _FileFinder):
            sys.path_hooks.pop(id)
            details = list(closure["loader_details"])
            yield details
            break
    sys.path_hooks.insert(id, FileFinder.path_hook(*details))
    sys.path_importer_cache.clear()


"""Update the file_finder details with functions to append and remove the [loader details](https://docs.python.org/3.7/library/importlib.html#importlib.machinery.FileFinder).
"""


def add_path_hooks(loader, extensions, *, position=0):
    """Update the FileFinder loader in sys.path_hooks to accomodate a {loader} with the {extensions}"""
    with modify_file_finder_details() as details:
        if position == -1:
            position = len(details)
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


class PathHooksContext(ExitStack):

    def __enter__(self, position=0):
        self = super().__enter__()
        add_path_hooks(self.prepare(self), self.EXTENSION_SUFFIXES, position=position)
        if getattr(self, "dir", None):
            self.enter_context(change_dir(self.dir))
            self.enter_context(modify_sys_path(self.dir))
        return self

    def __exit__(self, *excepts):
        remove_one_path_hook(self), super().__exit__(*excepts)

    def prepare(self, loader):
        if getattr(self, "lazy", None):
            try:
                from importlib.util import LazyLoader

                if self.lazy:
                    loader = LazyLoader.factory(loader)
            except:
                ImportWarning("""LazyLoading is only available in > Python 3.5""")
        return loader


@contextmanager
def change_dir(dir):
    next = Path().absolute()
    dir = Path(dir)
    if dir.absolute() != next:
        yield os.chdir(str(dir))
        os.chdir(str(next))
    else:
        yield None


@contextmanager
def modify_sys_path(file):
    """This is only invoked when using from_resource."""
    path = str(Path(file).parent)
    if path not in map(str, map(Path, sys.path)):
        yield sys.path.insert(0, path)
        sys.path = [object for object in sys.path if str(Path(object)) != path]
    else:
        yield


"""# Developer
"""

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("path_hooks.ipynb", "../path_hooks.py")
    import path_hooks

    print(__import__("doctest").testmod(path_hooks))
