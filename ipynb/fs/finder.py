"""
Contains the finder for use with filesystems.
"""
import sys
import os

from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec


class FSFinder(MetaPathFinder):
    """
    Finder for ipynb/py files from the filesystem.

    Only tries to load modules that are under ipynb.fs.
    Tries to treat .ipynb and .py files exactly the same as much as possible.

    The loader_class passed in to the constructor is used to do actual loading
    """
    def __init__(self, package_prefix, loader_class):
        self.loader_class = loader_class
        self.package_prefix = package_prefix

    def _get_paths(self, fullname):
        """
        Generate ordered list of paths we should look for fullname module in
        """
        real_path = os.path.join(*fullname[len(self.package_prefix):].split('.'))
        for base_path in sys.path:
            if base_path == '':
                # Empty string means process's cwd
                base_path = os.getcwd()
            path = os.path.join(base_path, real_path)
            yield path + '.ipynb'
            yield path + '.py'
            yield os.path.join(path, '__init__.ipynb')
            yield os.path.join(path, '__init__.py')

    def find_spec(self, fullname, path, target=None):
        """
        Claims modules that are under ipynb.fs
        """
        if fullname.startswith(self.package_prefix):
            for path in self._get_paths(fullname):
                if os.path.exists(path):
                    return ModuleSpec(
                        name=fullname,
                        loader=self.loader_class(fullname, path),
                        origin=path,
                        is_package=(path.endswith('__init__.ipynb') or path.endswith('__init__.py')),
                    )
