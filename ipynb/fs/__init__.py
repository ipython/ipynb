"""
FileSystem based importer for ipynb / .py files.

If you prefix module names with 'ipynb.fs', it'll try to treat them exactly
the same way as .py files. All the output is ignored, and all the code is imported
as if the cells were linearly written to be in a flat file.
"""
import sys
import os

from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec, SourceFileLoader

from ipynb.utils import get_code


class NotebookLoader(SourceFileLoader):
    def get_code(self, fullname):
        if self.path.endswith('.ipynb'):
            with open(self.path) as f:
                return self.source_to_code(get_code(f.read()), self.path)
        else:
            return super().get_code(fullname)


class FSFinder(MetaPathFinder):
    """
    Finder for ipynb/py files from the filesystem.

    Only tries to load modules that are under ipynb.fs.
    Tries to treat .ipynb and .py files exactly the same as much as possible.

    NotebookLoader is used to do the actual loading.
    """
    def _get_paths(self, fullname):
        """
        Generate ordered list of paths we should look for fullname module in
        """
        real_path = os.path.join(*fullname[len(__package__):].split('.'))
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
        if fullname.startswith(__package__):
            for path in self._get_paths(fullname):
                try:
                    if os.path.exists(path):
                        # It'll be the loader's responsibility to close file
                        return ModuleSpec(
                            name=fullname,
                            loader=NotebookLoader(fullname, path),
                            origin=path,
                            is_package=(path.endswith('__init__.ipynb') or path.endswith('__init__.py')),
                        )
                except FileNotFoundError:
                    continue

sys.meta_path.append(FSFinder())
