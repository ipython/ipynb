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
    id, details = get_loader_details()
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
                    file = Path(sorted(files)[0])
                    spec = super().find_spec(
                        (original + "." + file.stem.split(".", 1)[0]).lstrip("."), target=target
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


def get_loader_details():
    for id, path_hook in enumerate(sys.path_hooks):
        try:
            return id, list(inspect.getclosurevars(path_hook).nonlocals["loader_details"])
        except:
            continue


"""# Developer
"""

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("finder.ipynb", "../finder.py")
