# coding: utf-8
"""# `sys.path_hook` modifiers

Many suggestions for importing notebooks use `sys.meta_paths`, but `importnb` relies on the `sys.path_hooks` to load any notebook in the path. `PathHooksContext` is a base class for the `importnb.Notebook` `SourceFileLoader`.
"""

import inspect, sys, ast, os
from pathlib import Path

try:
    from importlib._bootstrap_external import FileFinder
except:
    # python 3.4
    from importlib.machinery import FileFinder

from contextlib import contextmanager, ExitStack

from itertools import chain

from importlib.machinery import SourceFileLoader, ModuleSpec


class FileModuleSpec(ModuleSpec):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_fileattr = True


class FuzzySpec(FileModuleSpec):

    def __init__(
        self, name, loader, *, alias=None, origin=None, loader_state=None, is_package=None
    ):
        super().__init__(
            name, loader, origin=origin, loader_state=loader_state, is_package=is_package
        )
        self.alias = alias


def fuzzy_query(str):
    new = ""
    for chr in str:
        new += (not new.endswith("__") or chr != "_") and chr or ""
    return new.replace("__", "*").replace("_", "?")


def fuzzy_file_search(path, fullname):
    results = []
    with modify_file_finder_details(None) as details:
        for ext in sum((list(object[1]) for object in details), []):
            results.extend(Path(path).glob(fullname + ext))
            "_" in fullname and results.extend(Path(path).glob(fuzzy_query(fullname) + ext))
    return results


class FuzzyFinder(FileFinder):
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
                files = fuzzy_file_search(self.path, fullname)
                if files:
                    files = sorted(files)
                    spec = super().find_spec(
                        (original + "." + Path(files[0]).stem.split(".", 1)[0]).lstrip("."),
                        target=target,
                    )
                    fullname = (original + "." + fullname).lstrip(".")
                    if spec and fullname != spec.name:
                        spec = FuzzySpec(
                            spec.name,
                            spec.loader,
                            origin=spec.origin,
                            loader_state=spec.loader_state,
                            alias=fullname,
                            is_package=bool(spec.submodule_search_locations),
                        )
        return spec


@contextmanager
def modify_file_finder_details(finder=FileFinder):
    """yield the FileFinder in the sys.path_hooks that loads Python files and assure
    the import cache is cleared afterwards.  
    
    * Everything goes to shit if the import cache is not cleared.
    * This function is independent
    
    When finder is None we just recieve the details
    
    """

    for id, hook in enumerate(sys.path_hooks):
        try:
            closure = inspect.getclosurevars(hook).nonlocals
        except TypeError:
            continue
        if issubclass(closure["cls"], FileFinder):
            finder and sys.path_hooks.pop(id)
            details = list(closure["loader_details"])
            yield details
            break

    if finder:
        # This repetition may eventually become a problem
        sys.path_hooks.insert(id, finder.path_hook(*details))
        sys.path_importer_cache.clear()


"""Update the file_finder details with functions to append and remove the [loader details](https://docs.python.org/3.7/library/importlib.html#importlib.machinery.FileFinder).
"""


def unwrap_loader(loader):
    """Extract the loader contents of a lazy loader in the import path."""
    try:
        return inspect.getclosurevars(loader).nonlocals.get("cls", loader)
    except:
        return loader


"""The Finder with add a finder factory the sys.path closure containing the filefinder.
"""


class BaseFinder(ExitStack):
    __slots__ = "finder", "lazy"

    def __init__(self, *, fuzzy=True, lazy=False, extensions=None):
        self.finder = fuzzy and FuzzyFinder or FileFinder
        self.lazy = lazy
        self.extensions = extensions or self.extensions or tuple()
        super().__init__()

    def __enter__(self, position=0):
        self = super().__enter__()
        self.add_path_hooks(self.prepare(self), self.extensions, position=position)
        if getattr(self, "dir", None):
            self.enter_context(change_dir(self.dir))
            self.enter_context(modify_sys_path(self.dir))
        return self

    def __exit__(self, *excepts):
        self.remove_one_path_hook(self)
        super().__exit__(*excepts)

    def prepare(self, loader):
        """Wrap the loader in a LazyLoader."""
        if getattr(self, "lazy", None):
            try:
                from importlib.util import LazyLoader

                if self.lazy:
                    loader = LazyLoader.factory(loader)
            except:
                ImportWarning("""LazyLoading is only available in > Python 3.5""")
        return loader

    def add_path_hooks(self, loader, extensions, *, position=0):
        """Update the FileFinder loader in sys.path_hooks to accomodate a {loader} with the {extensions}"""
        with modify_file_finder_details(self.finder) as details:
            if position == -1:
                position = len(details)
            details.insert(position, (loader, extensions))

    def remove_one_path_hook(self, loader):
        loader = unwrap_loader(loader)
        with modify_file_finder_details(self.finder) as details:
            _details = list(details)
            for ct, (cls, ext) in enumerate(_details):
                cls = unwrap_loader(cls)
                if cls == loader:
                    details.pop(ct)
                    break


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
    export("finder.ipynb", "../finder.py")
